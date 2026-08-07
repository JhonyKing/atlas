"""In-process answer-run coordinator used by local development and offline evaluation."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Protocol, cast
from uuid import UUID, uuid4

from atlas.api.answer_events import SSEEventWriter
from atlas.api.routes.answers import AnswerRunConflict, AnswerRunStatus
from atlas.domain import (
    AnswerDraft,
    AnswerStatus,
    CollectionSlug,
    Evidence,
    Question,
    assemble_citations,
)
from atlas.observability.langsmith import NullTraceSink, TraceSink
from atlas.persistence.quota import QuotaService


class AnswerGraph(Protocol):
    async def ainvoke(self, state: Mapping[str, object]) -> Mapping[str, object]: ...


@dataclass(slots=True)
class _Run:
    run_id: UUID
    visitor_key_hash: str
    idempotency_key: str
    question: Question
    request_id: UUID
    status: AnswerRunStatus
    queue: asyncio.Queue[str | None] = field(default_factory=asyncio.Queue)
    task: asyncio.Task[None] | None = None


class InMemoryAnswerRunService:
    """Coordinate one-shot graph execution with repeat-safe idempotency and cancellation."""

    def __init__(
        self,
        graph: AnswerGraph,
        *,
        quota: QuotaService | None = None,
        clock: Callable[[], datetime] | None = None,
        trace_sink: TraceSink | None = None,
        trace_metadata: Mapping[str, object] | None = None,
    ) -> None:
        self._graph = graph
        self._quota = quota
        self._clock = clock or (lambda: datetime.now(UTC))
        self._trace_sink = trace_sink or NullTraceSink()
        self._trace_metadata = dict(trace_metadata or {})
        self._runs: dict[UUID, _Run] = {}
        self._idempotency: dict[tuple[str, str], UUID] = {}
        self._lock = asyncio.Lock()

    async def start(
        self,
        *,
        question: Mapping[str, object],
        visitor_key_hash: str,
        idempotency_key: str,
        request_id: UUID,
    ) -> UUID:
        question_data = dict(question)
        product = question_data.get("product")
        if isinstance(product, str):
            question_data["product"] = CollectionSlug(product)
        for date_key in ("date_from", "date_to"):
            date_value = question_data.get(date_key)
            if isinstance(date_value, str):
                question_data[date_key] = date.fromisoformat(date_value)
        parsed_question = Question.model_validate(question_data)
        key = (visitor_key_hash, idempotency_key)
        async with self._lock:
            existing_id = self._idempotency.get(key)
            if existing_id is not None:
                existing = self._runs[existing_id]
                if existing.question != parsed_question:
                    raise KeyError(idempotency_key)
                return existing_id

            run_id = uuid4()
            now = self._clock()
            remaining = None
            if self._quota is not None:
                reservation = self._quota.reserve(
                    visitor_key_hash,
                    idempotency_key,
                    run_id,
                    now=now,
                )
                remaining = reservation.remaining
                run_id = reservation.run_id
            status = AnswerRunStatus(run_id=run_id, status="accepted", created_at=now)
            entry = _Run(
                run_id=run_id,
                visitor_key_hash=visitor_key_hash,
                idempotency_key=idempotency_key,
                question=parsed_question,
                request_id=request_id,
                status=status,
            )
            self._runs[run_id] = entry
            self._idempotency[key] = run_id
            writer = SSEEventWriter()
            entry.queue.put_nowait(
                writer.emit(
                    "run.accepted",
                    {
                        "run_id": str(run_id),
                        "stage": "accepted",
                        "quota": {
                            "limit": 10,
                            "remaining": remaining,
                            "window_hours": 24,
                        },
                    },
                )
            )
            entry.task = asyncio.create_task(self._execute(entry, writer))
            return run_id

    async def get_status(
        self,
        run_id: UUID,
        *,
        visitor_key_hash: str,
    ) -> AnswerRunStatus | None:
        entry = self._runs.get(run_id)
        if entry is None or entry.visitor_key_hash != visitor_key_hash:
            return None
        return entry.status

    async def cancel(self, run_id: UUID, *, visitor_key_hash: str) -> AnswerRunStatus:
        entry = self._runs.get(run_id)
        if entry is None or entry.visitor_key_hash != visitor_key_hash:
            raise KeyError(run_id)
        if entry.status.status in {"completed", "abstained", "failed"}:
            raise AnswerRunConflict("answer run is already terminal")
        if entry.status.status == "cancelled":
            return entry.status
        entry.status = entry.status.model_copy(update={"status": "cancelling"})
        if entry.task is not None:
            entry.task.cancel()
        entry.status = entry.status.model_copy(
            update={"status": "cancelled", "completed_at": self._clock()}
        )
        entry.queue.put_nowait(
            SSEEventWriter(sequence=1).emit(
                "answer.cancelled",
                {"run_id": str(run_id), "stage": "cancelled"},
            )
        )
        entry.queue.put_nowait(None)
        return entry.status

    async def stream(self, run_id: UUID, *, visitor_key_hash: str) -> AsyncIterator[str]:
        entry = self._runs.get(run_id)
        if entry is None or entry.visitor_key_hash != visitor_key_hash:
            raise KeyError(run_id)
        while True:
            frame = await entry.queue.get()
            if frame is None:
                return
            yield frame

    async def _execute(self, entry: _Run, writer: SSEEventWriter) -> None:
        root_trace = self._trace_sink.start(
            "atlas.answer",
            request_id=entry.request_id,
            run_id=entry.run_id,
            fields={
                **self._trace_metadata,
                "locale": entry.question.language,
                "question_length": len(entry.question.text),
            },
            tags=("answer", entry.question.language),
        )
        retrieval_trace = self._trace_sink.start(
            "atlas.retrieval",
            request_id=entry.request_id,
            run_id=entry.run_id,
            run_type="retriever",
            parent=root_trace,
        )
        generation_trace = self._trace_sink.start(
            "atlas.generation",
            request_id=entry.request_id,
            run_id=entry.run_id,
            run_type="llm",
            parent=root_trace,
        )
        verification_trace = self._trace_sink.start(
            "atlas.verification",
            request_id=entry.request_id,
            run_id=entry.run_id,
            parent=root_trace,
        )
        entry.status = entry.status.model_copy(update={"status": "retrieving"})
        entry.queue.put_nowait(
            writer.emit(
                "retrieval.started",
                {"run_id": str(entry.run_id), "stage": "retrieving"},
            )
        )
        try:
            result = await self._graph.ainvoke(
                {"question": entry.question, "request_id": entry.run_id}
            )
        except asyncio.CancelledError:
            self._trace_sink.end(retrieval_trace, status="cancelled")
            self._trace_sink.end(generation_trace, status="cancelled")
            self._trace_sink.end(verification_trace, status="cancelled")
            self._trace_sink.end(root_trace, status="cancelled")
            if entry.status.status != "cancelled":
                entry.status = entry.status.model_copy(
                    update={"status": "cancelled", "completed_at": self._clock()}
                )
                entry.queue.put_nowait(None)
            return

        self._trace_sink.end(retrieval_trace, status="completed")
        self._trace_sink.end(generation_trace, status="completed")

        answer = cast(AnswerDraft | None, result.get("answer"))
        evidence = cast(tuple[Evidence, ...] | list[Evidence], result.get("evidence", []))
        if answer is None or answer.answer_status is AnswerStatus.ABSTAINED:
            self._trace_sink.end(verification_trace, status="abstained")
            limitations = answer.limitations if answer is not None else []
            completed_at = self._clock()
            entry.status = entry.status.model_copy(
                update={
                    "status": "abstained",
                    "completed_at": completed_at,
                    "answer_status": "abstained",
                    "limitations": limitations,
                    "retained_until": completed_at + timedelta(days=30),
                }
            )
            entry.queue.put_nowait(
                writer.emit(
                    "answer.abstained",
                    {
                        "run_id": str(entry.run_id),
                        "stage": "abstained",
                        "limitations": limitations,
                    },
                )
            )
        else:
            self._trace_sink.end(verification_trace, status="completed")
            citations = [
                citation.model_dump(mode="json")
                for citation in assemble_citations(
                    evidence, evidence_ids=answer.evidence_ids
                )
            ]
            claims = [claim.model_dump(mode="json") for claim in answer.claims]
            completed_at = self._clock()
            entry.status = entry.status.model_copy(
                update={
                    "status": "completed",
                    "completed_at": completed_at,
                    "answer_status": answer.answer_status.value,
                    "claims": claims,
                    "citations": citations,
                    "limitations": answer.limitations,
                    "retained_until": completed_at + timedelta(days=30),
                }
            )
            entry.queue.put_nowait(
                writer.emit(
                    "answer.completed",
                    {
                        "run_id": str(entry.run_id),
                        "stage": "completed",
                        "answer_status": answer.answer_status.value,
                        "claims": [claim.model_dump(mode="json") for claim in answer.claims],
                        "citations": citations,
                        "limitations": answer.limitations,
                    },
                )
            )
        entry.queue.put_nowait(None)
        self._trace_sink.end(
            root_trace,
            status=entry.status.status,
            fields={"citation_count": len(entry.status.citations)},
        )
