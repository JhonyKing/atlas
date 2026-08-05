from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import cast
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


def service_for(graph: FakeGraph) -> InMemoryAnswerRunService:
    quota = QuotaService(
        InMemoryQuotaRepository(limit=10, window=timedelta(hours=24)),
    )
    return InMemoryAnswerRunService(cast(CitedAnswerGraph, graph), quota=quota)


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

