from __future__ import annotations

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
    ControlledError,
    ErrorCode,
    Evidence,
    Question,
    SourceType,
    VerificationStatus,
)
from atlas.providers.ports import ProviderRefusal
from atlas.retrieval.service import RetrievalRow

EVIDENCE_ID = UUID("00000000-0000-0000-0000-000000000701")


def evidence() -> Evidence:
    return Evidence(
        id=EVIDENCE_ID,
        source_title="Official docs",
        publisher="Publisher",
        canonical_url=HttpUrl("https://docs.example.test/reference"),
        excerpt="Captured support.",
        captured_at=datetime(2026, 8, 4, tzinfo=UTC),
        source_type=SourceType.DOCUMENTATION,
    )


class Embeddings:
    dimensions = 2

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


class Retriever:
    def __init__(self, rows: list[RetrievalRow]) -> None:
        self.rows = rows

    async def retrieve(
        self,
        question: Question,
        embedding: list[float],
        *,
        top_k: int = 8,
    ) -> list[RetrievalRow]:
        del question, embedding, top_k
        return self.rows


class Generator:
    def __init__(self, draft: AnswerDraft) -> None:
        self.draft = draft

    async def generate(
        self,
        question: Question,
        evidence: Sequence[Evidence],
        *,
        request_id: UUID | None = None,
    ) -> AnswerDraft:
        del question, evidence, request_id
        return self.draft


def graph_for(draft: AnswerDraft) -> CitedAnswerGraph:
    return CitedAnswerGraph(
        CitedAnswerDependencies(
            embedding_provider=Embeddings(),
            retriever=Retriever([RetrievalRow(evidence=evidence(), fused_rank=1)]),
            answer_generator=Generator(draft),
        )
    )


def error_of(result: CitedAnswerState) -> ControlledError:
    error = result.get("error")
    assert isinstance(error, ControlledError)
    return error


def answer_of(result: CitedAnswerState) -> AnswerDraft:
    answer = result.get("answer")
    assert isinstance(answer, AnswerDraft)
    return answer


@pytest.mark.asyncio
async def test_claim_without_evidence_abstains() -> None:
    claim = Claim.model_construct(
        id=uuid4(),
        ordinal=0,
        text="A claim without a citation.",
        type=ClaimType.FACTUAL,
        citation_ids=[],
    )
    draft = AnswerDraft.model_construct(
        answer_status=AnswerStatus.COMPLETE,
        claims=[claim],
        evidence_ids=[EVIDENCE_ID],
        limitations=[],
    )

    result = await graph_for(draft).ainvoke({"question": Question(text="What is supported?")})

    assert answer_of(result).answer_status is AnswerStatus.ABSTAINED
    assert error_of(result).code is ErrorCode.CITATION_VERIFICATION_FAILED


@pytest.mark.asyncio
async def test_contradictory_claim_abstains_with_disagreement_notice() -> None:
    claim = Claim.model_construct(
        id=uuid4(),
        ordinal=0,
        text="The sources disagree.",
        type=ClaimType.FACTUAL,
        citation_ids=[EVIDENCE_ID],
        verification_status=VerificationStatus.CONTRADICTED,
    )
    draft = AnswerDraft.model_construct(
        answer_status=AnswerStatus.COMPLETE,
        claims=[claim],
        evidence_ids=[EVIDENCE_ID],
        limitations=[],
    )

    result = await graph_for(draft).ainvoke(
        {"question": Question(text="Which version is correct?")}
    )

    assert answer_of(result).answer_status is AnswerStatus.ABSTAINED
    assert error_of(result).code is ErrorCode.CITATION_VERIFICATION_FAILED
    assert "contradict" in answer_of(result).limitations[0].lower()


@pytest.mark.asyncio
async def test_partial_draft_excludes_unsupported_claims_and_explains_gap() -> None:
    supported = Claim.model_construct(
        id=uuid4(),
        ordinal=0,
        text="The supported part.",
        type=ClaimType.FACTUAL,
        citation_ids=[EVIDENCE_ID],
        verification_status=VerificationStatus.SUPPORTED,
    )
    unsupported = Claim.model_construct(
        id=uuid4(),
        ordinal=1,
        text="The unsupported part.",
        type=ClaimType.FACTUAL,
        citation_ids=[EVIDENCE_ID],
        verification_status=VerificationStatus.UNSUPPORTED,
    )
    draft = AnswerDraft.model_construct(
        answer_status=AnswerStatus.PARTIAL,
        claims=[supported, unsupported],
        evidence_ids=[EVIDENCE_ID],
        limitations=[],
    )

    result = await graph_for(draft).ainvoke(
        {"question": Question(text="What is partly supported?")}
    )

    answer = answer_of(result)
    assert answer.answer_status is AnswerStatus.PARTIAL
    assert [claim.text for claim in answer.claims] == ["The supported part."]
    assert any("evidence" in limitation.lower() for limitation in answer.limitations)


class RefusingGenerator(Generator):
    async def generate(
        self,
        question: Question,
        evidence: Sequence[Evidence],
        *,
        request_id: UUID | None = None,
    ) -> AnswerDraft:
        del question, evidence, request_id
        raise ProviderRefusal("the question is outside the supported corpus")


@pytest.mark.asyncio
async def test_controlled_provider_refusal_is_not_reported_as_a_server_failure() -> None:
    graph = CitedAnswerGraph(
        CitedAnswerDependencies(
            embedding_provider=Embeddings(),
            retriever=Retriever([RetrievalRow(evidence=evidence(), fused_rank=1)]),
            answer_generator=RefusingGenerator(AnswerDraft.model_construct()),
        )
    )

    result = await graph.ainvoke({"question": Question(text="What is outside scope?")})

    assert answer_of(result).answer_status is AnswerStatus.ABSTAINED
    assert error_of(result).code is ErrorCode.UNSUPPORTED_QUESTION
