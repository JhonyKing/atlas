from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, cast
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl

from atlas.agent.cited_answer_graph import CitedAnswerGraph
from atlas.api.answer_service import InMemoryAnswerRunService
from atlas.domain import (
    AnswerDraft,
    AnswerStatus,
    Claim,
    ClaimType,
    Evidence,
    SourceType,
)
from atlas.observability.langsmith import TraceHandle, TraceSink
from atlas.persistence.quota import InMemoryQuotaRepository, QuotaService


def make_evidence(evidence_id: UUID) -> Evidence:
    return Evidence(
        id=evidence_id,
        source_title="Official docs",
        publisher="Official publisher",
        canonical_url=HttpUrl("https://docs.example.test/reference"),
        excerpt="Verified excerpt.",
        captured_at=datetime(2026, 8, 4, tzinfo=UTC),
        source_type=SourceType.DOCUMENTATION,
    )


class FakeGraph:
    def __init__(self, *, block: bool = False) -> None:
        self.block = block
        self.release = asyncio.Event()
        self.evidence_id = uuid4()

    async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
        if self.block:
            await self.release.wait()
        evidence = make_evidence(self.evidence_id)
        draft = AnswerDraft(
            answer_status=AnswerStatus.COMPLETE,
            evidence_ids=[evidence.id],
            claims=[
                Claim(
                    id=uuid4(),
                    ordinal=0,
                    text="Verified claim.",
                    type=ClaimType.FACTUAL,
                    citation_ids=[evidence.id],
                )
            ],
        )
        return {"answer": draft, "evidence": [evidence], "question": state["question"]}


class RecordingTraceSink:
    def __init__(self) -> None:
        self.started: list[dict[str, object]] = []
        self.ended: list[dict[str, object]] = []
        self.names: dict[UUID, str] = {}

    def start(
        self,
        name: str,
        *,
        request_id: UUID,
        run_id: UUID,
        run_type: Literal["chain", "llm", "retriever", "tool", "parser"] = "chain",
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        tags: Sequence[str] = (),
        parent: TraceHandle | None = None,
    ) -> TraceHandle:
        handle = TraceHandle(run_id=uuid4(), active=True)
        self.names[handle.run_id] = name
        self.started.append(
            {
                "name": name,
                "request_id": request_id,
                "run_id": run_id,
                "run_type": run_type,
                "fields": dict(fields or {}),
                "inputs": dict(inputs or {}),
                "tags": tuple(tags),
                "parent": parent,
            }
        )
        return handle

    def end(
        self,
        handle: TraceHandle,
        *,
        status: str,
        fields: Mapping[str, Any] | None = None,
        inputs: Mapping[str, Any] | None = None,
        outputs: Mapping[str, Any] | None = None,
    ) -> None:
        self.ended.append(
            {
                "name": self.names[handle.run_id],
                "status": status,
                "fields": dict(fields or {}),
                "inputs": dict(inputs or {}),
                "outputs": dict(outputs or {}),
            }
        )


def service_for(
    graph: FakeGraph,
    *,
    trace_sink: TraceSink | None = None,
) -> InMemoryAnswerRunService:
    quota = QuotaService(
        InMemoryQuotaRepository(limit=10, window=timedelta(hours=24)),
    )
    return InMemoryAnswerRunService(
        cast(CitedAnswerGraph, graph), quota=quota, trace_sink=trace_sink
    )


@pytest.mark.asyncio
async def test_service_is_idempotent_and_streams_terminal_verified_content() -> None:
    service = service_for(FakeGraph())
    request = {
        "text": "What is LangGraph?",
        "product": "langgraph",
    }

    first = await service.start(
        question=request,
        visitor_key_hash="a" * 64,
        idempotency_key="answer-service-key-001",
        request_id=uuid4(),
    )
    repeated = await service.start(
        question=request,
        visitor_key_hash="a" * 64,
        idempotency_key="answer-service-key-001",
        request_id=uuid4(),
    )
    frames = [frame async for frame in service.stream(first, visitor_key_hash="a" * 64)]

    assert first == repeated
    assert any("event: run.accepted" in frame for frame in frames)
    assert any("event: answer.completed" in frame for frame in frames)
    assert frames[-1].endswith("\n\n")


@pytest.mark.asyncio
async def test_service_traces_question_evidence_answer_and_verification() -> None:
    sink = RecordingTraceSink()
    service = service_for(FakeGraph(), trace_sink=sink)
    run_id = await service.start(
        question={"text": "What is LangGraph?", "product": "langgraph"},
        visitor_key_hash="c" * 64,
        idempotency_key="answer-service-trace-001",
        request_id=uuid4(),
    )

    _ = [frame async for frame in service.stream(run_id, visitor_key_hash="c" * 64)]

    started = {cast(str, item["name"]): item for item in sink.started}
    for name in ("atlas.answer", "atlas.retrieval", "atlas.generation"):
        assert cast(dict[str, object], started[name]["inputs"])["question"] == {
            "text": "What is LangGraph?",
            "product": "langgraph",
            "version": None,
            "date_from": None,
            "date_to": None,
            "language": "en-US",
        }

    ended = {cast(str, item["name"]): item for item in sink.ended}
    retrieval_outputs = cast(dict[str, object], ended["atlas.retrieval"]["outputs"])
    assert "Verified excerpt." in repr(retrieval_outputs["evidence"])
    generation_outputs = cast(dict[str, object], ended["atlas.generation"]["outputs"])
    assert "Verified claim." in repr(generation_outputs["answer"])
    verification_outputs = cast(dict[str, object], ended["atlas.verification"]["outputs"])
    assert "supported" in repr(verification_outputs["verification"])
    root_outputs = cast(dict[str, object], ended["atlas.answer"]["outputs"])
    assert set(root_outputs) == {"answer", "evidence", "verification"}


@pytest.mark.asyncio
async def test_service_cancellation_is_repeat_safe() -> None:
    service = service_for(FakeGraph(block=True))
    run_id = await service.start(
        question={"text": "Cancel this run"},
        visitor_key_hash="b" * 64,
        idempotency_key="answer-service-key-002",
        request_id=uuid4(),
    )

    first = await service.cancel(run_id, visitor_key_hash="b" * 64)
    repeated = await service.cancel(run_id, visitor_key_hash="b" * 64)

    assert first.status == "cancelled"
    assert repeated.status == "cancelled"
    frames = [frame async for frame in service.stream(run_id, visitor_key_hash="b" * 64)]
    assert any("event: answer.cancelled" in frame for frame in frames)
