"""In-process report coordinator for the first local vertical slice."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4

from psycopg import Connection
from psycopg.types.json import Jsonb

from atlas.reports.observability import ReportTraceMetadata
from atlas.reports.planner import ComparisonSource, ReportPlanningError, plan_report
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
        entry.trace_metadata = ReportTraceMetadata(
            request_id=entry.job.request_id,
            report_id=entry.job.report_id,
            source_run_id=entry.job.spec.source_run_id,
            model=entry.job.model,
            prompt_version=entry.job.prompt_version,
            corpus_snapshot=entry.job.corpus_snapshot,
        )
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


class PostgresReportService:
    """Persist report jobs and small generated documents in PostgreSQL for serverless runtimes."""

    def __init__(
        self,
        *,
        connection: Connection,
        source: ComparisonSource,
        limit: int = 3,
        window: timedelta = timedelta(hours=24),
        clock: Callable[[], datetime] | None = None,
        model: str = "gpt-5.6-luna",
        prompt_version: str = "report-v1",
    ) -> None:
        self._connection = connection
        self._source = source
        self._limit = limit
        self._window = window
        self._clock = clock or (lambda: datetime.now(UTC))
        self._model = model
        self._prompt_version = prompt_version

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
        now = self._clock()
        expires_at = now + timedelta(days=30)
        try:
            self._set_owner(owner_key_hash)
            previous = self._connection.execute(
                """SELECT id, spec FROM atlas.report_jobs
                   WHERE visitor_key_hash = %s AND idempotency_key = %s""",
                (owner_key_hash, idempotency_key),
            ).fetchone()
            if previous is not None:
                old_fingerprint = hashlib.sha256(
                    json.dumps(previous[1], sort_keys=True).encode()
                ).hexdigest()
                if old_fingerprint != fingerprint:
                    self._connection.rollback()
                    raise ValueError("idempotency_conflict")
                self._connection.commit()
                return cast(UUID, previous[0])
            count_row = self._connection.execute(
                """SELECT count(*) FROM atlas.report_jobs
                   WHERE visitor_key_hash = %s AND created_at > %s""",
                (owner_key_hash, now - self._window),
            ).fetchone()
            if count_row is None:
                raise RuntimeError("report quota query returned no result")
            count = int(count_row[0])
            if count >= self._limit:
                self._connection.rollback()
                raise ReportQuotaExceeded
            report_id = uuid4()
            inserted = self._connection.execute(
                """
                INSERT INTO atlas.report_jobs(
                  id, request_id, visitor_key_hash, source_run_id, report_type, locale,
                  spec, status, idempotency_key, created_at, expires_at, model, prompt_version
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'planning', %s, %s, %s, %s, %s)
                ON CONFLICT (visitor_key_hash, idempotency_key) DO NOTHING
                RETURNING id
                """,
                (
                    report_id,
                    request_id,
                    owner_key_hash,
                    spec.source_run_id,
                    spec.report_type.value,
                    spec.locale.value,
                    Jsonb(spec.model_dump(mode="json")),
                    idempotency_key,
                    now,
                    expires_at,
                    self._model,
                    self._prompt_version,
                ),
            ).fetchone()
            if inserted is None:
                self._connection.rollback()
                return await self._existing_idempotency(
                    owner_key_hash, idempotency_key, fingerprint
                )
            self._connection.commit()
        except (ReportQuotaExceeded, ValueError):
            raise
        except Exception:
            self._connection.rollback()
            raise

        try:
            representation = await plan_report(
                spec, owner_key_hash=owner_key_hash, source=self._source, clock=self._clock
            )
            validate_representation(representation)
            self._set_owner(owner_key_hash)
            self._connection.execute(
                """UPDATE atlas.report_jobs SET status = 'rendering'
                   WHERE id = %s AND visitor_key_hash = %s""",
                (report_id, owner_key_hash),
            )
            for file_format, content in (
                ("docx", render_docx(representation)),
                ("pdf", render_pdf(representation)),
            ):
                if file_format == "docx":
                    validate_docx(content, representation)
                else:
                    validate_pdf(content, representation)
                digest = hashlib.sha256(content).hexdigest()
                self._connection.execute(
                    """
                    INSERT INTO atlas.report_documents(
                      report_job_id, format, storage_key, content_hash, size_bytes,
                      created_at, expires_at, content
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (report_job_id, format) DO UPDATE SET
                      storage_key = EXCLUDED.storage_key, content_hash = EXCLUDED.content_hash,
                      size_bytes = EXCLUDED.size_bytes, created_at = EXCLUDED.created_at,
                      expires_at = EXCLUDED.expires_at, content = EXCLUDED.content
                    """,
                    (
                        report_id,
                        file_format,
                        f"database:{report_id}:{file_format}",
                        digest,
                        len(content),
                        now,
                        expires_at,
                        content,
                    ),
                )
            self._connection.execute(
                """UPDATE atlas.report_jobs SET status = 'completed', completed_at = %s
                   WHERE id = %s AND visitor_key_hash = %s""",
                (self._clock(), report_id, owner_key_hash),
            )
            self._connection.commit()
        except Exception as exc:
            self._connection.rollback()
            error_code = (
                str(exc) if isinstance(exc, ReportPlanningError) else "report_generation_failed"
            )
            try:
                self._set_owner(owner_key_hash)
                self._connection.execute(
                    """UPDATE atlas.report_jobs
                       SET status = 'failed', completed_at = %s, error_code = %s
                       WHERE id = %s AND visitor_key_hash = %s""",
                    (self._clock(), error_code[:160], report_id, owner_key_hash),
                )
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise
        return report_id

    async def _existing_idempotency(self, owner: str, key: str, fingerprint: str) -> UUID:
        self._set_owner(owner)
        row = self._connection.execute(
            """SELECT id, spec FROM atlas.report_jobs
               WHERE visitor_key_hash = %s AND idempotency_key = %s""",
            (owner, key),
        ).fetchone()
        if row is None:
            self._connection.commit()
            raise RuntimeError("report idempotency record disappeared")
        if hashlib.sha256(json.dumps(row[1], sort_keys=True).encode()).hexdigest() != fingerprint:
            self._connection.rollback()
            raise ValueError("idempotency_conflict")
        self._connection.commit()
        return cast(UUID, row[0])

    async def get(self, report_id: UUID, *, owner_key_hash: str) -> ReportJob:
        self._set_owner(owner_key_hash)
        row = self._connection.execute(
            """SELECT id, request_id, visitor_key_hash, spec, status, created_at,
                      completed_at, expires_at, model, prompt_version, corpus_snapshot, error_code
               FROM atlas.report_jobs WHERE id = %s AND visitor_key_hash = %s""",
            (report_id, owner_key_hash),
        ).fetchone()
        if row is None:
            self._connection.rollback()
            raise ReportNotFound(report_id)
        if (
            ReportStatus(row[4]) in {ReportStatus.COMPLETED, ReportStatus.FAILED}
            and self._clock() >= row[7]
        ):
            self._connection.execute(
                "UPDATE atlas.report_jobs SET status = 'expired' WHERE id = %s",
                (report_id,),
            )
            self._connection.execute(
                "DELETE FROM atlas.report_documents WHERE report_job_id = %s", (report_id,)
            )
            self._connection.commit()
            row = (*row[:4], ReportStatus.EXPIRED.value, *row[5:])
        document = self._document(report_id)
        self._connection.commit()
        return ReportJob(
            report_id=row[0],
            request_id=row[1],
            owner_key_hash=row[2].strip(),
            spec=ReportSpec.model_validate(row[3]),
            status=ReportStatus(row[4]),
            created_at=row[5],
            completed_at=row[6],
            expires_at=row[7],
            model=row[8],
            prompt_version=row[9],
            corpus_snapshot=row[10],
            document=document,
            error_code=row[11],
        )

    async def delete(self, report_id: UUID, *, owner_key_hash: str) -> ReportJob:
        job = await self.get(report_id, owner_key_hash=owner_key_hash)
        self._set_owner(owner_key_hash)
        self._connection.execute(
            """UPDATE atlas.report_jobs SET status = 'deleted'
               WHERE id = %s AND visitor_key_hash = %s""",
            (report_id, owner_key_hash),
        )
        self._connection.execute(
            "DELETE FROM atlas.report_documents WHERE report_job_id = %s", (report_id,)
        )
        self._connection.commit()
        return job.model_copy(update={"status": ReportStatus.DELETED, "document": None})

    async def download(
        self, report_id: UUID, *, owner_key_hash: str, format: str
    ) -> tuple[bytes, ReportJob]:
        job = await self.get(report_id, owner_key_hash=owner_key_hash)
        if job.status is not ReportStatus.COMPLETED or format not in {"docx", "pdf"}:
            raise ReportNotFound(report_id)
        self._set_owner(owner_key_hash)
        row = self._connection.execute(
            """SELECT content, content_hash FROM atlas.report_documents
               WHERE report_job_id = %s AND format = %s""",
            (report_id, format),
        ).fetchone()
        if row is None:
            self._connection.rollback()
            raise ReportNotFound(report_id)
        self._connection.commit()
        if row[0] is None or hashlib.sha256(row[0]).hexdigest() != row[1].strip():
            raise RuntimeError("stored report content hash does not match")
        return bytes(row[0]), job

    async def stream(self, report_id: UUID, *, owner_key_hash: str) -> AsyncIterator[str]:
        job = await self.get(report_id, owner_key_hash=owner_key_hash)
        yield json.dumps({"event": f"report.{job.status.value}", "status": job.status.value})

    def _document(self, report_id: UUID) -> ReportDocument | None:
        row = self._connection.execute(
            """SELECT d.format, d.content_hash, d.size_bytes, d.expires_at
               FROM atlas.report_documents d
               JOIN atlas.report_jobs j ON j.id = d.report_job_id
               WHERE d.report_job_id = %s
               ORDER BY (d.format = (j.spec->>'format')) DESC LIMIT 1""",
            (report_id,),
        ).fetchone()
        if row is None:
            return None
        from atlas.reports.schemas import ReportFormat

        return ReportDocument(
            format=ReportFormat(row[0]),
            content_hash=row[1].strip(),
            size_bytes=row[2],
            expires_at=row[3],
            download_name=f"atlas-report-{report_id}.{row[0]}",
        )

    def _set_owner(self, owner_key_hash: str) -> None:
        self._connection.execute(
            "SELECT set_config('atlas.visitor_key_hash', %s, true)", (owner_key_hash,)
        )
