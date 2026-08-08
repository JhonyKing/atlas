"""Append-only, content-safe lifecycle events for agent runs."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

EventType = Literal[
    "run.accepted",
    "plan.created",
    "approval.requested",
    "approval.decided",
    "tool_call.started",
    "tool_call.completed",
    "tool_call.abstained",
    "tool_call.failed",
    "verification.completed",
    "run.completed",
    "run.abstained",
    "run.cancelled",
    "run.failed",
    "run.resumed",
]


class AgentRunEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: UUID
    sequence: int = Field(ge=1)
    event_type: EventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: UUID = Field(default_factory=uuid4)
    tool_id: str | None = None
    tool_version: str | None = None
    call_id: str | None = None
    status: str = Field(min_length=1, max_length=64)
    evidence_ids: tuple[str, ...] = ()
    artifact_ids: tuple[str, ...] = ()
    error_category: str | None = None
    trace_id: str | None = None


class EventSequenceError(RuntimeError):
    """Events must be appended in sequence and cannot be rewritten."""


class InMemoryEventStore:
    def __init__(self) -> None:
        self._events: dict[UUID, list[AgentRunEvent]] = {}

    def append(self, event: AgentRunEvent) -> AgentRunEvent:
        current = self._events.setdefault(event.run_id, [])
        expected = len(current) + 1
        if event.sequence != expected:
            raise EventSequenceError(f"expected sequence {expected}, got {event.sequence}")
        current.append(event)
        return event

    def emit(
        self,
        run_id: UUID,
        event_type: EventType,
        *,
        status: str,
        **kwargs: object,
    ) -> AgentRunEvent:
        sequence = len(self._events.get(run_id, [])) + 1
        payload: dict[str, object] = {
            "run_id": run_id,
            "sequence": sequence,
            "event_type": event_type,
            "status": status,
        }
        payload.update(kwargs)
        event = AgentRunEvent.model_validate(payload)
        return self.append(event)

    def list(self, run_id: UUID, *, after_sequence: int = 0) -> tuple[AgentRunEvent, ...]:
        return tuple(
            event for event in self._events.get(run_id, ()) if event.sequence > after_sequence
        )

    def all(self, run_id: UUID) -> Iterable[AgentRunEvent]:
        return tuple(self._events.get(run_id, ()))
