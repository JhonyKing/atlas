"""Separate anonymous quota primitives for technology comparisons."""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol
from uuid import UUID

from psycopg import Connection


@dataclass(frozen=True, slots=True)
class ComparisonQuotaReservation:
    run_id: UUID
    remaining: int
    accepted_at: datetime
    is_new: bool = True


class ComparisonQuotaExceeded(RuntimeError):
    """The visitor has no accepted comparison reservations left in the window."""

    def __init__(self, retry_at: datetime) -> None:
        super().__init__("anonymous comparison quota exceeded")
        self.retry_at = retry_at

    def retry_after_seconds(self, *, now: datetime) -> int:
        seconds = (self.retry_at - _aware(now)).total_seconds()
        return max(1, math.ceil(seconds))


class ComparisonQuotaRepository(Protocol):
    def get_idempotent(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        *,
        now: datetime,
    ) -> ComparisonQuotaReservation | None: ...

    def reserve(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        run_id: UUID,
        *,
        now: datetime,
    ) -> ComparisonQuotaReservation: ...


class ComparisonQuotaService:
    """Application-facing comparison quota; it never consumes answer quota."""

    def __init__(self, repository: ComparisonQuotaRepository) -> None:
        self._repository = repository
        self._lock = threading.RLock()

    def reserve(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        run_id: UUID,
        *,
        now: datetime,
    ) -> ComparisonQuotaReservation:
        with self._lock:
            existing = self._repository.get_idempotent(visitor_key_hash, idempotency_key, now=now)
            if existing is not None:
                return existing
            return self._repository.reserve(visitor_key_hash, idempotency_key, run_id, now=now)


class InMemoryComparisonQuotaRepository:
    """Deterministic repository used by tests and offline evaluation."""

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
    ) -> ComparisonQuotaReservation:
        observed = _aware(now)
        with self._lock:
            self._events = [event for event in self._events if event[3] + self._window > observed]
            for visitor, key, existing_run, accepted_at, remaining in self._events:
                if visitor == visitor_key_hash and key == idempotency_key:
                    return ComparisonQuotaReservation(
                        existing_run, remaining, accepted_at, is_new=False
                    )
            visitor_events = [event for event in self._events if event[0] == visitor_key_hash]
            if len(visitor_events) >= self._limit:
                oldest = min(event[3] for event in visitor_events)
                raise ComparisonQuotaExceeded(oldest + self._window)
            remaining = self._limit - len(visitor_events) - 1
            self._events.append((visitor_key_hash, idempotency_key, run_id, observed, remaining))
            return ComparisonQuotaReservation(run_id, remaining, observed)

    def get_idempotent(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        *,
        now: datetime,
    ) -> ComparisonQuotaReservation | None:
        observed = _aware(now)
        with self._lock:
            for visitor, key, existing_run, accepted_at, remaining in self._events:
                if (
                    visitor == visitor_key_hash
                    and key == idempotency_key
                    and accepted_at + self._window > observed
                ):
                    return ComparisonQuotaReservation(
                        existing_run, remaining, accepted_at, is_new=False
                    )
        return None


class PostgresComparisonQuotaRepository:
    """Repository invoking the comparison-specific PostgreSQL function."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def reserve(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        run_id: UUID,
        *,
        now: datetime,
    ) -> ComparisonQuotaReservation:
        row = self._connection.execute(
            """
            SELECT accepted, run_id, remaining, accepted_at, retry_at
            FROM atlas.reserve_comparison_quota(%s, %s, %s, %s)
            """,
            (visitor_key_hash, idempotency_key, run_id, _aware(now)),
        ).fetchone()
        if row is None:
            raise RuntimeError("comparison quota function returned no result")
        if not row[0]:
            if row[4] is None:
                raise RuntimeError("comparison quota denial did not include retry time")
            raise ComparisonQuotaExceeded(row[4])
        self._connection.commit()
        return ComparisonQuotaReservation(row[1], row[2], row[3], is_new=row[1] == run_id)

    def get_idempotent(
        self,
        visitor_key_hash: str,
        idempotency_key: str,
        *,
        now: datetime,
    ) -> ComparisonQuotaReservation | None:
        row = self._connection.execute(
            """
            SELECT comparison_run_id, remaining_after, accepted_at
            FROM atlas.comparison_usage_events
            WHERE visitor_key_hash = %s
              AND idempotency_key = %s
              AND accepted_at > %s - interval '24 hours'
            """,
            (visitor_key_hash, idempotency_key, _aware(now)),
        ).fetchone()
        if row is None:
            return None
        return ComparisonQuotaReservation(row[0], row[1], row[2], is_new=False)


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
