"""Optional, content-minimized LangSmith tracing for ATLAS lifecycle runs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, Protocol
from uuid import UUID, uuid4

from atlas.config import Settings
from atlas.observability.telemetry import span_attributes

try:  # The dependency is declared, but imports stay optional for minimal tooling.
    from langsmith import Client
except ImportError:  # pragma: no cover - exercised only in a stripped runtime
    Client = None  # type: ignore[assignment,misc]

RunType = Literal["chain", "llm", "retriever", "tool", "parser"]


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
        tags: Sequence[str] = (),
        parent: TraceHandle | None = None,
    ) -> TraceHandle: ...

    def end(
        self,
        handle: TraceHandle,
        *,
        status: str,
        fields: Mapping[str, Any] | None = None,
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
        tags: Sequence[str] = (),
        parent: TraceHandle | None = None,
    ) -> TraceHandle:
        del name, request_id, run_type, fields, tags, parent
        return TraceHandle(run_id=run_id, active=False)

    def end(
        self,
        handle: TraceHandle,
        *,
        status: str,
        fields: Mapping[str, Any] | None = None,
    ) -> None:
        del handle, status, fields


class LangSmithTraceSink:
    """Best-effort LangSmith sink with strict content minimization.

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
                hide_inputs=True,
                hide_outputs=True,
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
        tags: Sequence[str] = (),
        parent: TraceHandle | None = None,
    ) -> TraceHandle:
        trace_id = uuid4()
        safe = span_attributes(request_id=request_id, operation=name, fields=fields)
        safe_metadata = {key.removeprefix("atlas."): value for key, value in safe.items()}
        try:
            self._client.create_run(
                id=trace_id,
                name=name,
                run_type=run_type,
                project_name=self._project,
                inputs={"request_id": str(request_id), "run_id": str(run_id)},
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
    ) -> None:
        if not handle.active:
            return
        safe = {key.removeprefix("atlas."): value for key, value in (fields or {}).items()}
        try:
            self._client.update_run(
                handle.run_id,
                outputs={"status": status, **safe},
                end_time=datetime.now(UTC),
            )
        except Exception:
            return
