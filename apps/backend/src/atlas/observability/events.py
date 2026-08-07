"""Redacted security lifecycle events for authenticated/private-data operations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from starlette.requests import Request

from atlas.observability.context import current_request_id
from atlas.privacy.redaction import redact_mapping


def ingestion_event(
    *,
    run_id: UUID,
    collection: str,
    outcome: str,
    latency_ms: float,
    error_code: str | None = None,
) -> dict[str, Any]:
    """Build content-free ingestion telemetry safe for logs and LangSmith tags."""

    event: dict[str, Any] = {
        "run_id": str(run_id),
        "collection": collection,
        "outcome": outcome,
        "latency_ms": round(max(latency_ms, 0.0), 2),
    }
    if error_code:
        event["error_code"] = error_code
    return event


def security_event(
    *,
    request_id: UUID,
    operation: str,
    subject_id: UUID | None,
    ownership_decision: str | None = None,
    fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a trace-safe event with stable correlation and no private payload."""

    event: dict[str, Any] = {
        "request_id": str(request_id),
        "operation": operation,
        "subject_id": str(subject_id) if subject_id else None,
    }
    if ownership_decision is not None:
        event["ownership_decision"] = ownership_decision
    if fields:
        event["fields"] = redact_mapping(fields)
    return event


def record_security_event(
    request: Request,
    *,
    operation: str,
    subject_id: UUID | None,
    ownership_decision: str | None = None,
    fields: Mapping[str, Any] | None = None,
) -> None:
    """Attach a redacted event to the request for the configured trace sink."""

    event = security_event(
        request_id=current_request_id() or UUID(int=0),
        operation=operation,
        subject_id=subject_id,
        ownership_decision=ownership_decision,
        fields=fields,
    )
    events = getattr(request.state, "security_events", None)
    if events is None:
        events = []
        request.state.security_events = events
    events.append(event)
