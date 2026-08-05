"""Anonymous rolling-window quota and global cost-budget primitives."""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from psycopg import Connection


@dataclass(frozen=True, slots=True)
class QuotaReservation:
    run_id: UUID
    remaining: int
    accepted_at: datetime
    is_new: bool = True


class QuotaExceeded(RuntimeError):
    """The visitor has no accepted answer reservations left in the current window."""

    def __init__(self, retry_at: datetime) -> None:
        super().__init__("anonymous answer quota exceeded")
        self.retry_at = retry_at

    def retry_after_seconds(self, *, now: datetime) -> int:
        seconds = (self.retry_at - _aware(now)).total_seconds()
        return max(1, math.ceil(seconds))


class BudgetExceeded(RuntimeError):
    """The process-wide daily model-cost budget is exhausted."""


class QuotaRepository(Protocol):
    def get_idempotent(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        *,
        now: datetime,
    ) -> QuotaReservation | None: ...

    def reserve(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        run_id: UUID,
        *,
        now: datetime,
    ) -> QuotaReservation: ...


class QuotaService:
    """Application-facing quota service; the repository owns the transaction boundary."""

    def __init__(
        self,
        repository: QuotaRepository,
        *,
        global_budget: GlobalDailyBudget | None = None,
    ) -> None:
        self._repository = repository
        self._global_budget = global_budget
        self._lock = threading.RLock()

    def reserve(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        run_id: UUID,
        *,
        now: datetime,
        estimated_cost_usd: Decimal | None = None,
    ) -> QuotaReservation:
        with self._lock:
            existing = self._repository.get_idempotent(
                visitor_key_hash,
                idempotency_key,
                now=now,
            )
            if existing is not None:
                return existing
            budget_reserved = False
            budget = self._global_budget
            if budget is not None and estimated_cost_usd is not None:
                budget.reserve(estimated_cost_usd, observed_at=now)
                budget_reserved = True
            try:
                reservation = self._repository.reserve(
                    visitor_key_hash,
                    idempotency_key,
                    run_id,
                    now=now,
                )
            except QuotaExceeded:
                if budget_reserved and estimated_cost_usd is not None:
                    assert budget is not None
                    budget.release(estimated_cost_usd, observed_at=now)
                raise
            if budget_reserved and not reservation.is_new and estimated_cost_usd is not None:
                assert budget is not None
                budget.release(estimated_cost_usd, observed_at=now)
            return reservation


class InMemoryQuotaRepository:
    """Deterministic, lock-protected repository for tests and local offline evaluation."""

    def __init__(self, *, limit: int, window: timedelta) -> None:
        if limit <= 0 or window <= timedelta(0):
            raise ValueError("quota limit and window must be positive")
        self._limit = limit
        self._window = window
        self._lock = threading.RLock()
        self._events: list[tuple[str, str, UUID, datetime, int]] = []

    def reserve(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        run_id: UUID,
        *,
        now: datetime,
    ) -> QuotaReservation:
        observed = _aware(now)
        with self._lock:
            self._events = [
                event
                for event in self._events
                if event[3] + self._window > observed
            ]
            for visitor, key, existing_run, accepted_at, remaining in self._events:
                if visitor == visitor_key_hash and key == idempotency_key:
                    return QuotaReservation(existing_run, remaining, accepted_at, is_new=False)

            visitor_events = [event for event in self._events if event[0] == visitor_key_hash]
            if len(visitor_events) >= self._limit:
                oldest = min(event[3] for event in visitor_events)
                raise QuotaExceeded(oldest + self._window)

            remaining = self._limit - len(visitor_events) - 1
            event = (visitor_key_hash, idempotency_key, run_id, observed, remaining)
            self._events.append(event)
            return QuotaReservation(run_id, remaining, observed)

    def get_idempotent(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        *,
        now: datetime,
    ) -> QuotaReservation | None:
        observed = _aware(now)
        with self._lock:
            for visitor, key, existing_run, accepted_at, remaining in self._events:
                if (
                    visitor == visitor_key_hash
                    and key == idempotency_key
                    and accepted_at + self._window > observed
                ):
                    return QuotaReservation(existing_run, remaining, accepted_at, is_new=False)
        return None

    def accepted_count(self, visitor_key_hash: str, now: datetime) -> int:
        observed = _aware(now)
        with self._lock:
            return sum(
                event[0] == visitor_key_hash and event[3] + self._window > observed
                for event in self._events
            )


class PostgresQuotaRepository:
    """Repository invoking the advisory-lock-backed PostgreSQL quota function."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def reserve(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        run_id: UUID,
        *,
        now: datetime,
    ) -> QuotaReservation:
        row = self._connection.execute(
            """
            SELECT accepted, run_id, remaining, accepted_at, retry_at
            FROM atlas.reserve_answer_quota(%s, %s, %s, %s)
            """,
            (visitor_key_hash, idempotency_key, run_id, _aware(now)),
        ).fetchone()
        if row is None:
            raise RuntimeError("quota function returned no result")
        if not row[0]:
            retry_at = row[4]
            if retry_at is None:
                raise RuntimeError("quota denial did not include retry time")
            raise QuotaExceeded(retry_at)
        self._connection.commit()
        return QuotaReservation(row[1], row[2], row[3], is_new=row[1] == run_id)

    def get_idempotent(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        *,
        now: datetime,
    ) -> QuotaReservation | None:
        row = self._connection.execute(
            """
            SELECT answer_run_id, remaining_after, accepted_at
            FROM atlas.usage_events
            WHERE visitor_key_hash = %s
              AND idempotency_key = %s
              AND accepted_at > %s - interval '24 hours'
            """,
            (visitor_key_hash, idempotency_key, _aware(now)),
        ).fetchone()
        if row is None:
            return None
        return QuotaReservation(row[0], row[1], row[2], is_new=False)


@dataclass(slots=True)
class GlobalDailyBudget:
    """Thread-safe in-process circuit breaker for estimated model cost."""

    limit_usd: Decimal
    _day: date | None = None
    _spent_usd: Decimal = Decimal("0")
    _lock: threading.Lock = dataclass_field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        if self.limit_usd <= 0:
            raise ValueError("daily budget must be positive")

    def reserve(self, amount_usd: Decimal, *, observed_at: datetime) -> None:
        if amount_usd < 0:
            raise ValueError("budget amount must not be negative")
        observed = _aware(observed_at)
        day = observed.date()
        with self._lock:
            if self._day != day:
                self._day = day
                self._spent_usd = Decimal("0")
            if self._spent_usd + amount_usd > self.limit_usd:
                raise BudgetExceeded("global daily model budget exhausted")
            self._spent_usd += amount_usd

    def release(self, amount_usd: Decimal, *, observed_at: datetime) -> None:
        """Roll back a reservation when the database quota rejects the same request."""

        observed = _aware(observed_at)
        with self._lock:
            if self._day == observed.date():
                self._spent_usd = max(Decimal("0"), self._spent_usd - amount_usd)

    def spent(self) -> Decimal:
        with self._lock:
            return self._spent_usd


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
