"""Optional, content-minimized LangSmith tracing for ATLAS lifecycle runs."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any, Literal, Protocol
from uuid import UUID, uuid4

from atlas.config import Settings
from atlas.observability.telemetry import safe_scalar_fields, span_attributes

try:  # The dependency is declared, but imports stay optional for minimal tooling.
    from langsmith import Client
except ImportError:  # pragma: no cover - exercised only in a stripped runtime
    Client = None  # type: ignore[assignment,misc]

RunType = Literal["chain", "llm", "retriever", "tool", "parser"]
TracePayload = (
    str | int | float | bool | None | list["TracePayload"] | dict[str, "TracePayload"]
)

_MAX_TRACE_DEPTH = 6
_MAX_TRACE_ITEMS = 20
_MAX_TRACE_FIELDS = 50
_MAX_TRACE_STRING_CHARS = 4_000
_REDACTED = "[REDACTED]"
_TRUNCATED = "[TRUNCATED]"
_SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "credential",
    "password",
    "private_key",
    "secret",
    "session",
    "token",
)
_SECRET_VALUE_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[a-zA-Z0-9_-]{8,}\b"),
    re.compile(r"\blsv2_[a-zA-Z0-9_-]{8,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|password|secret|token)=([^&\s]+)"),
)


def sanitize_trace_payload(payload: Mapping[str, Any] | None) -> dict[str, TracePayload]:
    """Bound functional trace content and recursively redact credential-shaped values."""

    if payload is None:
        return {}
    sanitized = _sanitize_trace_value(payload, depth=0)
    return sanitized if isinstance(sanitized, dict) else {}


def _sanitize_trace_value(value: Any, *, depth: int) -> TracePayload:
    if depth >= _MAX_TRACE_DEPTH:
        return _TRUNCATED
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, Enum):
        return _sanitize_trace_value(value.value, depth=depth)
    if isinstance(value, (UUID, date, datetime)):
        return value.isoformat() if not isinstance(value, UUID) else str(value)
    if isinstance(value, str):
        redacted = value
        for pattern in _SECRET_VALUE_PATTERNS:
            redacted = pattern.sub(_redact_secret_match, redacted)
        if len(redacted) > _MAX_TRACE_STRING_CHARS:
            return f"{redacted[:_MAX_TRACE_STRING_CHARS]}...{_TRUNCATED}"
        return redacted
    if isinstance(value, Mapping):
        result: dict[str, TracePayload] = {}
        for index, (raw_key, item) in enumerate(value.items()):
            if index >= _MAX_TRACE_FIELDS:
                result[_TRUNCATED] = f"additional fields omitted after {_MAX_TRACE_FIELDS}"
                break
            key = str(raw_key)
            normalized = key.casefold().replace("-", "_")
            if any(part in normalized for part in _SENSITIVE_KEY_PARTS):
                result[key] = _REDACTED
            else:
                result[key] = _sanitize_trace_value(item, depth=depth + 1)
        return result
    if isinstance(value, Sequence):
        items = [
            _sanitize_trace_value(item, depth=depth + 1)
            for item in value[:_MAX_TRACE_ITEMS]
        ]
        if len(value) > _MAX_TRACE_ITEMS:
            items.append(f"{len(value) - _MAX_TRACE_ITEMS} additional items {_TRUNCATED}")
        return items
    return f"[UNSUPPORTED:{type(value).__name__}]"


def _redact_secret_match(match: re.Match[str]) -> str:
    label = match.group(1) if match.lastindex else None
    return f"{label}={_REDACTED}" if label else _REDACTED


@dataclass(frozen=True, slots=True)
class TraceHandle:
    """Opaque handle used to complete one trace without exposing provider details."""

    run_id: UUID
    active: bool


class TraceSink(Protocol):
    def start(
        self,
        name: str,
        *,
        request_id: UUID,
        run_id: UUID,
        run_type: RunType = "chain",
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        tags: Sequence[str] = (),
        parent: TraceHandle | None = None,
    ) -> TraceHandle: ...

    def end(
        self,
        handle: TraceHandle,
        *,
        status: str,
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        outputs: Mapping[str, Any] | None = None,
    ) -> None: ...


class NullTraceSink:
    """No-op sink used in tests, local development and deployments without LangSmith."""

    def start(
        self,
        name: str,
        *,
        request_id: UUID,
        run_id: UUID,
        run_type: RunType = "chain",
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        tags: Sequence[str] = (),
        parent: TraceHandle | None = None,
    ) -> TraceHandle:
        del name, request_id, run_type, fields, inputs, tags, parent
        return TraceHandle(run_id=run_id, active=False)

    def end(
        self,
        handle: TraceHandle,
        *,
        status: str,
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        outputs: Mapping[str, Any] | None = None,
    ) -> None:
        del handle, status, fields, inputs, outputs


class LangSmithTraceSink:
    """Best-effort LangSmith sink with bounded evaluation content and secret redaction.

    The sink deliberately swallows SDK/network failures. Local OpenTelemetry and the answer API
    remain authoritative, so a tracing outage cannot make a user request fail.
    """

    def __init__(self, client: Any, *, project: str) -> None:
        self._client = client
        self._project = project

    @classmethod
    def from_settings(cls, settings: Settings) -> TraceSink:
        key = settings.langsmith_api_key
        if not settings.langsmith_tracing or key is None or not key.get_secret_value().strip():
            return NullTraceSink()
        if Client is None:  # pragma: no cover - defensive for stripped deployments
            return NullTraceSink()
        try:
            client = Client(
                api_key=key.get_secret_value(),
                api_url=(str(settings.langsmith_endpoint) if settings.langsmith_endpoint else None),
                workspace_id=settings.langsmith_workspace_id,
                # ATLAS sanitizes payloads before they reach the SDK. Keep those approved
                # functional evaluation payloads visible in LangSmith after recursive redaction.
                hide_inputs=False,
                hide_outputs=False,
            )
        except Exception:
            return NullTraceSink()
        return cls(client, project=settings.langsmith_project)

    def start(
        self,
        name: str,
        *,
        request_id: UUID,
        run_id: UUID,
        run_type: RunType = "chain",
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        tags: Sequence[str] = (),
        parent: TraceHandle | None = None,
    ) -> TraceHandle:
        trace_id = uuid4()
        safe = span_attributes(request_id=request_id, operation=name, fields=fields)
        safe_metadata = {key.removeprefix("atlas."): value for key, value in safe.items()}
        safe_inputs = sanitize_trace_payload(inputs)
        try:
            self._client.create_run(
                id=trace_id,
                name=name,
                run_type=run_type,
                project_name=self._project,
                inputs={"request_id": str(request_id), "run_id": str(run_id), **safe_inputs},
                extra={"metadata": safe_metadata},
                tags=list(tags),
                parent_run_id=parent.run_id if parent and parent.active else None,
                start_time=datetime.now(UTC),
            )
        except Exception:
            return TraceHandle(run_id=trace_id, active=False)
        return TraceHandle(run_id=trace_id, active=True)

    def end(
        self,
        handle: TraceHandle,
        *,
        status: str,
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        outputs: Mapping[str, Any] | None = None,
    ) -> None:
        if not handle.active:
            return
        safe = safe_scalar_fields(fields)
        safe_inputs = sanitize_trace_payload(inputs)
        safe_outputs = sanitize_trace_payload(outputs)
        update: dict[str, Any] = {
            "outputs": {**safe, **safe_outputs, "status": status},
            "end_time": datetime.now(UTC),
        }
        if inputs is not None:
            update["inputs"] = safe_inputs
        try:
            self._client.update_run(handle.run_id, **update)
        except Exception:
            return
