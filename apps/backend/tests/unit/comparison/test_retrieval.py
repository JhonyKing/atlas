from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from pydantic import HttpUrl

from atlas.comparison.retrieval import ComparisonRetrievalService
from atlas.comparison.schemas import ComparisonCriterion, ComparisonRequest
from atlas.domain import CollectionSlug, Evidence, SourceType
from atlas.retrieval.service import RetrievalRow


def _evidence(title: str) -> Evidence:
    return Evidence(
        id=uuid4(),
        source_title=title,
        publisher="ATLAS test",
        canonical_url=HttpUrl("https://example.com/" + title.casefold()),
        excerpt="Evidence excerpt",
        captured_at=datetime(2026, 8, 5, 12, tzinfo=UTC),
        source_type=SourceType.DOCUMENTATION,
    )


class FakeComparisonRetriever:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def retrieve_branch(self, **kwargs: object) -> list[RetrievalRow]:
        self.calls.append(kwargs)
        technology = kwargs["technology"]
        criterion = kwargs["criterion"]
        first = RetrievalRow(evidence=_evidence(f"{technology}-{criterion}"), fused_rank=2)
        duplicate = RetrievalRow(evidence=first.evidence, fused_rank=3)
        return [duplicate, first]


def test_price_defaults_to_pricing_sources_when_no_override_is_given() -> None:
    request = ComparisonRequest(
        technologies=[CollectionSlug.OPENAI, CollectionSlug.ANTHROPIC],
        criteria=[ComparisonCriterion.PRICE],
        source_type=SourceType.DOCUMENTATION,
    )
    assert request.effective_source_type(ComparisonCriterion.PRICE) is SourceType.PRICING


@pytest.mark.asyncio
async def test_fan_out_keeps_technology_criterion_order_and_selected_snapshot() -> None:
    retriever = FakeComparisonRetriever()
    service = ComparisonRetrievalService(retriever)
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.CAPABILITY, ComparisonCriterion.PRICE],
        version="1.0",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 8, 5),
        source_type=SourceType.DOCUMENTATION,
    )

    branches = await service.retrieve(
        request,
        snapshot_id=uuid4(),
        embeddings={criterion: [0.1, 0.2] for criterion in request.criteria},
        top_k=4,
    )

    assert [(branch.technology, branch.criterion) for branch in branches] == [
        (CollectionSlug.LANGGRAPH, ComparisonCriterion.CAPABILITY),
        (CollectionSlug.LANGGRAPH, ComparisonCriterion.PRICE),
        (CollectionSlug.OPENAI, ComparisonCriterion.CAPABILITY),
        (CollectionSlug.OPENAI, ComparisonCriterion.PRICE),
    ]
    assert all(len(branch.rows) == 1 for branch in branches)
    assert all(call["snapshot_id"] == branches[0].snapshot_id for call in retriever.calls)
    assert all(call["version"] == "1.0" for call in retriever.calls)
    assert all(call["date_from"] == date(2026, 1, 1) for call in retriever.calls)
    assert all(call["date_to"] == date(2026, 8, 5) for call in retriever.calls)
    price_calls = [call for call in retriever.calls if call["criterion"] is ComparisonCriterion.PRICE]
    assert all(call["source_type"] is SourceType.PRICING for call in price_calls)


@pytest.mark.asyncio
async def test_fan_out_does_not_mix_evidence_between_technology_branches() -> None:
    retriever = FakeComparisonRetriever()
    service = ComparisonRetrievalService(retriever)
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGCHAIN, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.CONTEXT],
    )

    branches = await service.retrieve(
        request,
        snapshot_id=uuid4(),
        embeddings={ComparisonCriterion.CONTEXT: [0.3]},
    )

    assert branches[0].rows[0].evidence.source_title.startswith("langchain-")
    assert branches[1].rows[0].evidence.source_title.startswith("openai-")
