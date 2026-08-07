"""Anonymous comparison run coordinator with fail-closed runtime wiring."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Callable, Mapping
from datetime import UTC, date, datetime, timedelta
from typing import Protocol, cast
from uuid import UUID, uuid4

from atlas.api.routes.comparisons import ComparisonRunResponse
from atlas.comparison.events import ComparisonEventWriter
from atlas.comparison.observability import ComparisonTraceTree
from atlas.comparison.schemas import (
    ComparisonMatrix,
    ComparisonRequest,
    ComparisonRun,
    ComparisonRunStatus,
)
from atlas.observability.langsmith import NullTraceSink, TraceSink
from atlas.persistence.comparison_quota import ComparisonQuotaService
from atlas.persistence.comparison_repository import InMemoryComparisonRepository


class ComparisonExecutor(Protocol):
    async def run(
        self,
        comparison: ComparisonRequest,
        *,
        snapshot_id: UUID,
        is_cancelled: Callable[[], bool],
    ) -> ComparisonMatrix: ...


class _Entry:
    def __init__(self, run: ComparisonRun, *, comparison: ComparisonRequest) -> None:
        self.run = run
        self.comparison = comparison
        self.queue: asyncio.Queue[str | None] = asyncio.Queue()
        self.task: asyncio.Task[None] | None = None
        self.cancelled = False
        self.matrix: ComparisonMatrix | None = None
        self.accepted_monotonic = time.perf_counter()


class InMemoryComparisonRunService:
    """Coordinate comparison lifecycle; absent executors fail closed without publishing data."""

    def __init__(
        self,
        *,
        quota: ComparisonQuotaService,
        repository: InMemoryComparisonRepository,
        snapshot_provider: Callable[[], UUID],
        executor: ComparisonExecutor | None = None,
        clock: Callable[[], datetime] | None = None,
        trace_sink: TraceSink | None = None,
        model: str = "gpt-5.6-luna",
    ) -> None:
        self._quota = quota
        self._repository = repository
        self._snapshot_provider = snapshot_provider
        self._executor = executor
        self._clock = clock or (lambda: datetime.now(UTC))
        self._trace_sink = trace_sink or NullTraceSink()
        self._model = model
        self._entries: dict[UUID, _Entry] = {}
        self._idempotency: dict[tuple[str, str], UUID] = {}
        self._lock = asyncio.Lock()

    async def start(
        self,
        *,
        comparison: Mapping[str, object],
        visitor_key_hash: str,
        idempotency_key: str,
        request_id: UUID,
    ) -> UUID:
        parsed = _parse_request(comparison)
        key = (visitor_key_hash, idempotency_key)
        async with self._lock:
            existing = self._idempotency.get(key)
            if existing is not None:
                return existing
            run_id = uuid4()
            reservation = self._quota.reserve(
                visitor_key_hash, idempotency_key, run_id, now=self._clock()
            )
            run_id = reservation.run_id
            now = self._clock()
            run = ComparisonRun(
                run_id=run_id,
                request_id=request_id,
                visitor_key_hash=visitor_key_hash,
                snapshot_id=self._snapshot_provider(),
                status=ComparisonRunStatus.ACCEPTED,
                created_at=now,
                retained_until=now + timedelta(days=30),
            )
            self._repository.create(run, idempotency_key=idempotency_key)
            entry = _Entry(run, comparison=parsed)
            self._entries[run_id] = entry
            self._idempotency[key] = run_id
            writer = ComparisonEventWriter(run_id=run_id)
            entry.queue.put_nowait(writer.emit("comparison.accepted", {"status": "accepted"}))
            entry.task = asyncio.create_task(self._execute(entry, writer))
            return run_id

    async def get_status(
        self, run_id: UUID, *, visitor_key_hash: str
    ) -> ComparisonRunResponse | None:
        entry = self._entries.get(run_id)
        if entry is None or entry.run.visitor_key_hash != visitor_key_hash:
            return None
        return self._response(entry)

    async def cancel(self, run_id: UUID, *, visitor_key_hash: str) -> ComparisonRunResponse:
        entry = self._entries.get(run_id)
        if entry is None or entry.run.visitor_key_hash != visitor_key_hash:
            raise KeyError(run_id)
        if entry.run.status in {
            ComparisonRunStatus.COMPLETED,
            ComparisonRunStatus.ABSTAINED,
            ComparisonRunStatus.FAILED,
        }:
            return self._response(entry)
        entry.cancelled = True
        if entry.task is not None:
            entry.task.cancel()
        entry.run = entry.run.model_copy(
            update={"status": ComparisonRunStatus.CANCELLED, "completed_at": self._clock()}
        )
        writer = ComparisonEventWriter(run_id=run_id)
        writer.emit("comparison.accepted", {"status": "accepted"})
        entry.queue.put_nowait(writer.emit("comparison.cancelled", {"status": "cancelled"}))
        entry.queue.put_nowait(None)
        return self._response(entry)

    async def stream(self, run_id: UUID, *, visitor_key_hash: str) -> AsyncIterator[str]:
        entry = self._entries.get(run_id)
        if entry is None or entry.run.visitor_key_hash != visitor_key_hash:
            raise KeyError(run_id)
        while True:
            frame = await entry.queue.get()
            if frame is None:
                return
            yield frame

    async def _execute(self, entry: _Entry, writer: ComparisonEventWriter) -> None:
        entry.queue.put_nowait(
            writer.emit(
                "comparison.retrieval.started",
                {
                    "status": "retrieving",
                    "elapsed_ms": max(
                        0, int((time.perf_counter() - entry.accepted_monotonic) * 1000)
                    ),
                },
            )
        )
        trace_tree = ComparisonTraceTree.start(
            self._trace_sink,
            request_id=entry.run.request_id,
            run_id=entry.run.run_id,
            locale=entry.comparison.language,
            technology_count=len(entry.comparison.technologies),
            criterion_count=len(entry.comparison.criteria),
            snapshot_id=entry.run.snapshot_id,
            model=self._model,
            quota_limit=5,
        )
        if self._executor is None:
            entry.run = entry.run.model_copy(
                update={"status": ComparisonRunStatus.FAILED, "completed_at": self._clock()}
            )
            entry.queue.put_nowait(
                writer.emit(
                    "comparison.failed", {"status": "failed", "reason": "executor_unavailable"}
                )
            )
            trace_tree.end(status="failed")
            entry.queue.put_nowait(None)
            return
        try:
            retrieval_trace = trace_tree.start_stage("retrieval")
            matrix = await self._executor.run(
                entry.comparison,
                snapshot_id=entry.run.snapshot_id,
                is_cancelled=lambda: entry.cancelled,
            )
            self._repository.save_matrix(entry.run.run_id, matrix)
            self._trace_sink.end(retrieval_trace, status="completed")
            entry.queue.put_nowait(
                writer.emit("comparison.retrieval.completed", {"status": "retrieving"})
            )
            entry.queue.put_nowait(
                writer.emit("comparison.normalization.completed", {"status": "normalizing"})
            )
            verification_trace = trace_tree.start_stage("verification")
            self._trace_sink.end(verification_trace, status="completed")
            entry.queue.put_nowait(
                writer.emit("comparison.verification.completed", {"status": "verifying"})
            )
            entry.matrix = matrix
            entry.run = entry.run.model_copy(
                update={"status": ComparisonRunStatus.COMPLETED, "completed_at": self._clock()}
            )
            self._repository.complete(
                entry.run.run_id,
                visitor_key_hash=entry.run.visitor_key_hash,
                completed_at=entry.run.completed_at or self._clock(),
            )
            entry.queue.put_nowait(
                writer.emit(
                    "comparison.completed",
                    {"status": "completed", "matrix": matrix.model_dump(mode="json")},
                )
            )
            trace_tree.end(status="completed", matrix_cell_count=len(matrix.cells))
        except asyncio.CancelledError:
            trace_tree.end(status="cancelled")
            return
        except Exception:
            entry.run = entry.run.model_copy(
                update={"status": ComparisonRunStatus.FAILED, "completed_at": self._clock()}
            )
            entry.queue.put_nowait(
                writer.emit("comparison.failed", {"status": "failed", "reason": "workflow_failed"})
            )
            trace_tree.end(status="failed")
        finally:
            entry.queue.put_nowait(None)

    @staticmethod
    def _response(entry: _Entry) -> ComparisonRunResponse:
        return ComparisonRunResponse(
            run_id=entry.run.run_id,
            status=entry.run.status.value,
            created_at=entry.run.created_at,
            completed_at=entry.run.completed_at,
            matrix=entry.matrix,
            retained_until=entry.run.retained_until,
        )


def _parse_request(raw: Mapping[str, object]) -> ComparisonRequest:
    payload = dict(raw)
    technologies = cast(list[object], payload.get("technologies", []))
    criteria = cast(list[object], payload.get("criteria", []))
    payload["technologies"] = [str(value) for value in technologies]
    payload["criteria"] = [str(value) for value in criteria]
    from atlas.comparison.schemas import ComparisonCriterion
    from atlas.domain import CollectionSlug, SourceType

    payload["technologies"] = [
        CollectionSlug(value) for value in cast(list[str], payload["technologies"])
    ]
    payload["criteria"] = [
        ComparisonCriterion(value) for value in cast(list[str], payload["criteria"])
    ]
    if payload.get("source_type") is not None:
        payload["source_type"] = SourceType(str(payload["source_type"]))
    if payload.get("product") is not None:
        payload["product"] = CollectionSlug(str(payload["product"]))
    for key in ("date_from", "date_to"):
        if isinstance(payload.get(key), str):
            payload[key] = date.fromisoformat(str(payload[key]))
    return ComparisonRequest.model_validate(payload)
