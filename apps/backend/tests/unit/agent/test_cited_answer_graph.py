from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl

from atlas.agent.cited_answer_graph import (
    CitedAnswerDependencies,
    CitedAnswerGraph,
    CitedAnswerState,
)
from atlas.domain import (
    AnswerDraft,
    AnswerStatus,
    Claim,
    ClaimType,
    CollectionSlug,
    ControlledError,
    ErrorCode,
    Evidence,
    Question,
    SourceType,
)
from atlas.retrieval.service import RetrievalRow


def make_evidence(evidence_id: UUID) -> Evidence:
    return Evidence(
        id=evidence_id,
        source_title="Official docs",
        publisher="Official publisher",
        canonical_url=HttpUrl("https://docs.example.test/reference"),
        excerpt="The official answer is supported here.",
        captured_at=datetime(2026, 8, 4, tzinfo=UTC),
        source_type=SourceType.DOCUMENTATION,
    )


def make_draft(evidence_id: UUID, *, invalid: bool = False) -> AnswerDraft:
    citation_id = uuid4() if invalid else evidence_id
    return AnswerDraft(
        answer_status=AnswerStatus.COMPLETE,
        evidence_ids=[evidence_id],
        claims=[
            Claim(
                id=uuid4(),
                ordinal=0,
                text="The answer is supported.",
                type=ClaimType.FACTUAL,
                citation_ids=[citation_id],
            )
        ],
    )


class FakeEmbeddingProvider:
    dimensions = 2

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


class FakeRetriever:
    def __init__(self, rows: list[RetrievalRow]) -> None:
        self.rows = rows
        self.questions: list[str] = []

    async def retrieve(
        self,
        question: Question,
        embedding: list[float],
        *,
        top_k: int = 8,
    ) -> list[RetrievalRow]:
        del embedding, top_k
        self.questions.append(question.text)
        return self.rows


class FakeAnswerGenerator:
    def __init__(self, draft: AnswerDraft, *, delay: float = 0.0) -> None:
        self.draft = draft
        self.delay = delay
        self.questions: list[str] = []

    async def generate(
        self,
        question: Question,
        evidence: Sequence[Evidence],
        *,
        request_id: UUID | None = None,
    ) -> AnswerDraft:
        del evidence, request_id
        self.questions.append(question.text)
        if self.delay:
            await asyncio.sleep(self.delay)
        return self.draft


def build_graph(
    rows: list[RetrievalRow],
    draft: AnswerDraft,
    *,
    timeout_seconds: float = 1.0,
) -> tuple[CitedAnswerGraph, FakeRetriever, FakeAnswerGenerator]:
    retriever = FakeRetriever(rows)
    generator = FakeAnswerGenerator(draft)
    graph = CitedAnswerGraph(
        CitedAnswerDependencies(
            embedding_provider=FakeEmbeddingProvider(),
            retriever=retriever,
            answer_generator=generator,
            timeout_seconds=timeout_seconds,
        )
    )
    return graph, retriever, generator


def answer_of(result: CitedAnswerState) -> AnswerDraft:
    answer = result.get("answer")
    assert answer is not None
    return answer


def error_of(result: CitedAnswerState) -> ControlledError:
    error = result.get("error")
    assert error is not None
    return error


@pytest.mark.asyncio
async def test_graph_orders_nodes_and_releases_only_verified_answer() -> None:
    evidence_id = uuid4()
    graph, retriever, generator = build_graph(
        [RetrievalRow(evidence=make_evidence(evidence_id), fused_rank=1)],
        make_draft(evidence_id),
    )

    result = await graph.ainvoke(
        {"question": Question(text="What is the answer?", product=CollectionSlug.LANGGRAPH)}
    )

    assert result["stage"] == "finalized"
    assert answer_of(result).answer_status is AnswerStatus.COMPLETE
    assert result["visited"] == [
        "validate",
        "retrieve",
        "evidence_gate",
        "compose",
        "verify",
        "finalize",
    ]
    assert retriever.questions == ["What is the answer?"]
    assert generator.questions == ["What is the answer?"]


@pytest.mark.asyncio
async def test_graph_state_is_isolated_between_runs() -> None:
    first_id = uuid4()
    second_id = uuid4()
    graph, _, generator = build_graph(
        [RetrievalRow(evidence=make_evidence(first_id), fused_rank=1)],
        make_draft(first_id),
    )

    first = await graph.ainvoke({"question": Question(text="First question")})
    generator.draft = make_draft(second_id)
    second = await graph.ainvoke({"question": Question(text="Second question")})

    assert first["question"].text == "First question"
    assert second["question"].text == "Second question"
    assert answer_of(first).evidence_ids == [first_id]
    assert first["visited"][-1] == "finalize"
    assert answer_of(second).answer_status is AnswerStatus.ABSTAINED
    assert second["visited"][-1] == "abstain"


@pytest.mark.asyncio
async def test_graph_abstains_when_model_invents_an_evidence_id() -> None:
    evidence_id = uuid4()
    graph, _, _ = build_graph(
        [RetrievalRow(evidence=make_evidence(evidence_id), fused_rank=1)],
        make_draft(evidence_id, invalid=True),
    )

    result = await graph.ainvoke({"question": Question(text="What is the answer?")})

    assert answer_of(result).answer_status is AnswerStatus.ABSTAINED
    assert error_of(result).code is ErrorCode.CITATION_VERIFICATION_FAILED
    assert "invented" in answer_of(result).limitations[0].lower()


@pytest.mark.asyncio
async def test_graph_abstains_without_evidence_and_does_not_call_model() -> None:
    graph, _, generator = build_graph([], make_draft(uuid4()))

    result = await graph.ainvoke({"question": Question(text="Unsupported question")})

    assert answer_of(result).answer_status is AnswerStatus.ABSTAINED
    assert error_of(result).code is ErrorCode.INSUFFICIENT_EVIDENCE
    assert generator.questions == []


@pytest.mark.asyncio
async def test_graph_converts_provider_timeout_to_controlled_abstention() -> None:
    evidence_id = uuid4()
    graph, _, generator = build_graph(
        [RetrievalRow(evidence=make_evidence(evidence_id), fused_rank=1)],
        make_draft(evidence_id),
        timeout_seconds=0.01,
    )
    generator.delay = 0.1

    result = await graph.ainvoke({"question": Question(text="Slow question")})

    assert answer_of(result).answer_status is AnswerStatus.ABSTAINED
    assert error_of(result).code is ErrorCode.PROVIDER_UNAVAILABLE


@pytest.mark.asyncio
async def test_graph_honors_cancellation_before_retrieval() -> None:
    graph, retriever, _ = build_graph([], make_draft(uuid4()))

    result = await graph.ainvoke(
        {"question": Question(text="Cancel me"), "cancelled": True}
    )

    assert answer_of(result).answer_status is AnswerStatus.ABSTAINED
    assert error_of(result).code is ErrorCode.CANCELLED
    assert retriever.questions == []
