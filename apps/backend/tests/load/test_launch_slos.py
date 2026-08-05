"""Small portfolio-launch smoke checks; these intentionally do not claim capacity."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from time import monotonic
from typing import cast
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl

from atlas.agent.cited_answer_graph import CitedAnswerGraph
from atlas.api.answer_service import InMemoryAnswerRunService
from atlas.domain import AnswerDraft, AnswerStatus, Claim, ClaimType, Evidence, SourceType
from atlas.persistence.quota import InMemoryQuotaRepository, QuotaExceeded, QuotaService


def _evidence(evidence_id: UUID) -> Evidence:
    return Evidence(
        id=evidence_id,
        source_title="Official docs",
        publisher="Publisher",
        canonical_url=HttpUrl("https://docs.example.test/reference"),
        excerpt="Verified excerpt.",
        captured_at=datetime(2026, 8, 4, tzinfo=UTC),
        source_type=SourceType.DOCUMENTATION,
    )


class FastGraph:
    async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
        del state
        evidence = _evidence(uuid4())
        return {
            "answer": AnswerDraft(
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
            ),
            "evidence": [evidence],
        }


class BlockingGraph(FastGraph):
    def __init__(self) -> None:
        self.release = asyncio.Event()

    async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
        await self.release.wait()
        return await super().ainvoke(state)


def _service(graph: FastGraph) -> InMemoryAnswerRunService:
    quota = QuotaService(InMemoryQuotaRepository(limit=10, window=timedelta(hours=24)))
    return InMemoryAnswerRunService(cast(CitedAnswerGraph, graph), quota=quota)


def test_bounded_burst_accepts_ten_and_rejects_the_next_reservation() -> None:
    repository = InMemoryQuotaRepository(limit=10, window=timedelta(hours=24))
    quota = QuotaService(repository)
    now = datetime(2026, 8, 4, 12, tzinfo=UTC)
    accepted = 0
    for index in range(20):
        try:
            quota.reserve("a" * 64, f"load-smoke-{index:03d}", uuid4(), now=now)
        except QuotaExceeded:
            continue
        accepted += 1

    assert accepted == 10
    assert repository.accepted_count("a" * 64, now) == 10


@pytest.mark.asyncio
async def test_bounded_concurrent_answers_complete_within_launch_budget() -> None:
    service = _service(FastGraph())
    started_at = monotonic()
    run_ids = await asyncio.gather(
        *(
            service.start(
                question={"text": "How does LangGraph work?"},
                visitor_key_hash=f"{index:064x}"[-64:],
                idempotency_key=f"load-answer-{index:03d}",
                request_id=uuid4(),
            )
            for index in range(10)
        )
    )
    frames = await asyncio.gather(
        *(_collect(service, run_id, f"{index:064x}"[-64:]) for index, run_id in enumerate(run_ids))
    )

    assert monotonic() - started_at < 15
    assert all(any("event: answer.completed" in frame for frame in stream) for stream in frames)


@pytest.mark.asyncio
async def test_cancellation_is_repeat_safe_for_a_bounded_active_run() -> None:
    service = _service(BlockingGraph())
    visitor = "c" * 64
    run_id = await service.start(
        question={"text": "Cancel this launch smoke run"},
        visitor_key_hash=visitor,
        idempotency_key="load-cancel-001",
        request_id=uuid4(),
    )

    first = await service.cancel(run_id, visitor_key_hash=visitor)
    repeated = await service.cancel(run_id, visitor_key_hash=visitor)
    frames = [frame async for frame in service.stream(run_id, visitor_key_hash=visitor)]

    assert first.status == "cancelled"
    assert repeated.status == "cancelled"
    assert any("event: answer.cancelled" in frame for frame in frames)


async def _collect(
    service: InMemoryAnswerRunService,
    run_id: UUID,
    visitor: str,
) -> list[str]:
    return [frame async for frame in service.stream(run_id, visitor_key_hash=visitor)]
