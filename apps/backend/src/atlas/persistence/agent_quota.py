"""Replay-safe rolling quota for private or mutating agent tools."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import RLock
from typing import Any, Protocol
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb


@dataclass(frozen=True, slots=True)
class AgentToolQuotaReservation:
    run_id: UUID
    call_id: str
    remaining: int
    reserved_at: datetime
    is_new: bool = True


class AgentToolQuotaExceeded(RuntimeError):
    """No new side-effect calls are available in the current window."""

    def __init__(self, retry_at: datetime) -> None:
        super().__init__("agent tool quota exceeded")
        self.retry_at = retry_at

    def retry_after_seconds(self, *, now: datetime) -> int:
        return max(1, math.ceil((self.retry_at - _aware(now)).total_seconds()))


class AgentToolQuotaConflict(ValueError):
    """An operation key was reused for a different tool call."""


class AgentToolQuotaRepository(Protocol):
    def reserve(
        self,
        visitor_key_hash: str,
        tool_id: str,
        idempotency_key: str,
        run_id: UUID,
        call_id: str,
        fingerprint: str,
        *,
        now: datetime,
    ) -> AgentToolQuotaReservation: ...


@dataclass(frozen=True, slots=True)
class _QuotaEvent:
    visitor_key_hash: str
    tool_id: str
    idempotency_key: str
    run_id: UUID
    call_id: str
    fingerprint: str
    remaining: int
    reserved_at: datetime


class InMemoryAgentToolQuotaRepository:
    """Lock-protected development implementation with durable-adapter semantics."""

    def __init__(self, *, limit: int, window: timedelta) -> None:
        if limit <= 0 or window <= timedelta(0):
            raise ValueError("agent tool quota limit and window must be positive")
        self._limit = limit
        self._window = window
        self._events: list[_QuotaEvent] = []
        self._lock = RLock()

    def reserve(
        self,
        visitor_key_hash: str,
        tool_id: str,
        idempotency_key: str,
        run_id: UUID,
        call_id: str,
        fingerprint: str,
        *,
        now: datetime,
    ) -> AgentToolQuotaReservation:
        observed = _aware(now)
        with self._lock:
            self._events = [
                event for event in self._events if event.reserved_at + self._window > observed
            ]
            for event in self._events:
                if (
                    event.visitor_key_hash == visitor_key_hash
                    and event.tool_id == tool_id
                    and event.idempotency_key == idempotency_key
                ):
                    if event.fingerprint != fingerprint:
                        raise AgentToolQuotaConflict(
                            "idempotency key conflicts with another agent tool call"
                        )
                    return AgentToolQuotaReservation(
                        event.run_id,
                        event.call_id,
                        event.remaining,
                        event.reserved_at,
                        is_new=False,
                    )
            matching = [
                event
                for event in self._events
                if event.visitor_key_hash == visitor_key_hash and event.tool_id == tool_id
            ]
            if len(matching) >= self._limit:
                raise AgentToolQuotaExceeded(
                    min(event.reserved_at for event in matching) + self._window
                )
            remaining = self._limit - len(matching) - 1
            self._events.append(
                _QuotaEvent(
                    visitor_key_hash,
                    tool_id,
                    idempotency_key,
                    run_id,
                    call_id,
                    fingerprint,
                    remaining,
                    observed,
                )
            )
            return AgentToolQuotaReservation(run_id, call_id, remaining, observed)


class PostgresAgentToolQuotaRepository:
    """Use the existing durable idempotency ledger as a per-owner/tool quota ledger."""

    owner_scoped = True

    def __init__(self, connection: Connection[Any], *, limit: int, window: timedelta) -> None:
        if limit <= 0 or window <= timedelta(0):
            raise ValueError("agent tool quota limit and window must be positive")
        self._connection = connection
        self._limit = limit
        self._window = window

    def reserve(
        self,
        visitor_key_hash: str,
        tool_id: str,
        idempotency_key: str,
        run_id: UUID,
        call_id: str,
        fingerprint: str,
        *,
        now: datetime,
    ) -> AgentToolQuotaReservation:
        observed = _aware(now)
        scope = _quota_scope(visitor_key_hash, tool_id)
        try:
            self._connection.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (scope,)
            )
            existing = self._connection.execute(
                """
                SELECT fingerprint, response, created_at
                FROM atlas.agent_idempotency_records
                WHERE scope = %s AND idempotency_key = %s
                """,
                (scope, idempotency_key),
            ).fetchone()
            if existing is not None:
                if str(existing[0]).strip() != fingerprint:
                    raise AgentToolQuotaConflict(
                        "idempotency key conflicts with another agent tool call"
                    )
                response = dict(existing[1] or {})
                self._connection.commit()
                return AgentToolQuotaReservation(
                    UUID(str(response["run_id"])),
                    str(response["call_id"]),
                    int(response["remaining"]),
                    _aware(existing[2]),
                    is_new=False,
                )
            cutoff = observed - self._window
            row = self._connection.execute(
                """
                SELECT count(*), min(created_at)
                FROM atlas.agent_idempotency_records
                WHERE scope = %s AND created_at > %s
                """,
                (scope, cutoff),
            ).fetchone()
            count = int(row[0]) if row is not None else 0
            oldest = row[1] if row is not None else None
            if count >= self._limit:
                self._connection.rollback()
                retry_at = _aware(oldest) + self._window if oldest is not None else observed
                raise AgentToolQuotaExceeded(retry_at)
            remaining = self._limit - count - 1
            response = {
                "run_id": str(run_id),
                "call_id": call_id,
                "tool_id": tool_id,
                "remaining": remaining,
                "reserved_at": observed.isoformat(),
            }
            self._connection.execute(
                """
                INSERT INTO atlas.agent_idempotency_records(
                  scope, idempotency_key, fingerprint, response, created_at
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (scope, idempotency_key, fingerprint, Jsonb(response), observed),
            )
            self._connection.commit()
            return AgentToolQuotaReservation(run_id, call_id, remaining, observed)
        except (AgentToolQuotaConflict, AgentToolQuotaExceeded):
            if not self._connection.closed:
                self._connection.rollback()
            raise


def _quota_scope(visitor_key_hash: str, tool_id: str) -> str:
    owner_tool = hashlib.sha256(f"{visitor_key_hash}:{tool_id}".encode()).hexdigest()[:48]
    return f"agent.quota:{owner_tool}"


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
