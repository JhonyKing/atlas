"""In-process report coordinator for the first local vertical slice."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from atlas.reports.observability import ReportTraceMetadata
from atlas.reports.planner import ComparisonSource, plan_report
from atlas.reports.renderers.docx import render_docx
from atlas.reports.renderers.pdf import render_pdf
from atlas.reports.schemas import ReportDocument, ReportJob, ReportSpec, ReportStatus
from atlas.reports.storage import LocalArtifactStorage
from atlas.reports.validation import (
    validate_docx,
    validate_pdf,
    validate_representation,
)


class ReportQuotaExceeded(RuntimeError):
    """The visitor reached the report limit."""


class ReportNotFound(KeyError):
    """The report is missing or not owned by the visitor."""


class _Entry:
    def __init__(self, job: ReportJob) -> None:
        self.job = job
        self.paths: dict[str, str] = {}
        self.events: asyncio.Queue[str | None] = asyncio.Queue()
        self.task: asyncio.Task[None] | None = None
        self.trace_metadata: ReportTraceMetadata | None = None


class InMemoryReportService:
    def __init__(
        self,
        *,
        source: ComparisonSource,
        storage: LocalArtifactStorage | None = None,
        limit: int = 3,
        window: timedelta = timedelta(hours=24),
        clock: Callable[[], datetime] | None = None,
        model: str = "gpt-5.6-luna",
        prompt_version: str = "report-v1",
    ) -> None:
        self._source = source
        self._storage = storage or LocalArtifactStorage(Path(".atlas-artifacts"))
        self._limit = limit
        self._window = window
        self._clock = clock or (lambda: datetime.now(UTC))
        self._model = model
        self._prompt_version = prompt_version
        self._entries: dict[UUID, _Entry] = {}
        self._idempotency: dict[tuple[str, str], tuple[str, UUID]] = {}
        self._reservations: dict[str, list[datetime]] = {}
        self._lock = asyncio.Lock()

    async def create(
        self,
        spec: ReportSpec,
        *,
        owner_key_hash: str,
        idempotency_key: str,
        request_id: UUID,
    ) -> UUID:
        fingerprint = hashlib.sha256(
            json.dumps(spec.model_dump(mode="json"), sort_keys=True).encode()
        ).hexdigest()
        key = (owner_key_hash, idempotency_key)
        async with self._lock:
            previous = self._idempotency.get(key)
            if previous is not None:
                if previous[0] != fingerprint:
                    raise ValueError("idempotency_conflict")
                return previous[1]
            now = self._clock()
            reservations = [
                value
                for value in self._reservations.get(owner_key_hash, [])
                if value > now - self._window
            ]
            if len(reservations) >= self._limit:
                raise ReportQuotaExceeded
            reservations.append(now)
            self._reservations[owner_key_hash] = reservations
            report_id = uuid4()
            job = ReportJob(
                report_id=report_id,
                request_id=request_id,
                owner_key_hash=owner_key_hash,
                spec=spec,
                status=ReportStatus.ACCEPTED,
                created_at=now,
                expires_at=now + timedelta(days=30),
                model=self._model,
                prompt_version=self._prompt_version,
            )
            self._entries[report_id] = _Entry(job)
            self._idempotency[key] = (fingerprint, report_id)
            self._entries[report_id].task = asyncio.create_task(self._run(report_id))
            return report_id

    async def get(self, report_id: UUID, *, owner_key_hash: str) -> ReportJob:
        entry = self._entries.get(report_id)
        if entry is None or entry.job.owner_key_hash != owner_key_hash:
            raise ReportNotFound(report_id)
        self._expire_if_needed(entry)
        return entry.job

    async def delete(self, report_id: UUID, *, owner_key_hash: str) -> ReportJob:
        entry = self._entries.get(report_id)
        if entry is None or entry.job.owner_key_hash != owner_key_hash:
            raise ReportNotFound(report_id)
        if entry.job.status is not ReportStatus.DELETED:
            for path in entry.paths.values():
                self._storage.delete(path)
            entry.job = entry.job.model_copy(update={"status": ReportStatus.DELETED})
        return entry.job

    async def download(
        self, report_id: UUID, *, owner_key_hash: str, format: str
    ) -> tuple[bytes, ReportJob]:
        job = await self.get(report_id, owner_key_hash=owner_key_hash)
        if job.status is not ReportStatus.COMPLETED or format not in {"docx", "pdf"}:
            raise ReportNotFound(report_id)
            entry = self._entries[report_id]
            entry.trace_metadata = ReportTraceMetadata(
                request_id=entry.job.request_id,
                report_id=entry.job.report_id,
                source_run_id=entry.job.spec.source_run_id,
                model=entry.job.model,
                prompt_version=entry.job.prompt_version,
                corpus_snapshot=entry.job.corpus_snapshot,
            )
        return self._storage.get(entry.paths[format]), job

    async def stream(self, report_id: UUID, *, owner_key_hash: str) -> AsyncIterator[str]:
        entry = self._entries.get(report_id)
        if entry is None or entry.job.owner_key_hash != owner_key_hash:
            raise ReportNotFound(report_id)
        while True:
            event = await entry.events.get()
            if event is None:
                return
            yield event

    async def _run(self, report_id: UUID) -> None:
        entry = self._entries[report_id]
        try:
            entry.job = entry.job.model_copy(update={"status": ReportStatus.PLANNING})
            entry.events.put_nowait('{"event":"report.planning","status":"planning"}')
            representation = await plan_report(
                entry.job.spec,
                owner_key_hash=entry.job.owner_key_hash,
                source=self._source,
                clock=self._clock,
            )
            validate_representation(representation)
            entry.job = entry.job.model_copy(update={"status": ReportStatus.RENDERING})
            entry.events.put_nowait('{"event":"report.rendering","status":"rendering"}')
            docx = render_docx(representation)
            pdf = render_pdf(representation)
            validate_docx(docx, representation)
            validate_pdf(pdf, representation)
            for suffix, content in (("docx", docx), ("pdf", pdf)):
                path, size, digest = self._storage.put(report_id, suffix, content)
                entry.paths[suffix] = path
                if suffix == entry.job.spec.format.value:
                    entry.job = entry.job.model_copy(
                        update={
                            "document": ReportDocument(
                                format=entry.job.spec.format,
                                content_hash=digest,
                                size_bytes=size,
                                expires_at=entry.job.expires_at,
                                download_name=f"atlas-report-{report_id}.{suffix}",
                            )
                        }
                    )
            entry.job = entry.job.model_copy(
                update={"status": ReportStatus.COMPLETED, "completed_at": self._clock()}
            )
            entry.events.put_nowait('{"event":"report.completed","status":"completed"}')
        except Exception as exc:
            entry.job = entry.job.model_copy(
                update={
                    "status": ReportStatus.FAILED,
                    "completed_at": self._clock(),
                    "error_code": str(exc),
                }
            )
            entry.events.put_nowait('{"event":"report.failed","status":"failed"}')
        finally:
            entry.events.put_nowait(None)

    def _expire_if_needed(self, entry: _Entry) -> None:
        if (
            entry.job.status in {ReportStatus.COMPLETED, ReportStatus.FAILED}
            and self._clock() >= entry.job.expires_at
        ):
            for path in entry.paths.values():
                self._storage.delete(path)
            entry.job = entry.job.model_copy(update={"status": ReportStatus.EXPIRED})
