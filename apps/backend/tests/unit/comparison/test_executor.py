from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from pydantic import HttpUrl

from atlas.comparison.executor import RetrievalComparisonExecutor
from atlas.comparison.normalization import ComparisonObservation
from atlas.comparison.retrieval import ComparisonRetrievalBranch, ComparisonRetrievalService
from atlas.comparison.schemas import ComparisonCriterion, ComparisonRequest
from atlas.domain import CollectionSlug, Evidence, SourceType
from atlas.retrieval.service import RetrievalRow


class FakeEmbeddingProvider:
    dimensions = 1

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[float(index + 1)] for index, _ in enumerate(texts)]


class FakeRetriever:
    async def retrieve_branch(
        self, *, technology: CollectionSlug, **kwargs: Any
    ) -> list[RetrievalRow]:
        del kwargs
        evidence = Evidence(
            id=uuid4(),
            source_title=f"{technology.value} docs",
            publisher="fixture",
            canonical_url=HttpUrl("https://example.com/docs"),
            excerpt="The feature is explicitly documented.",
            captured_at=datetime(2026, 8, 5, tzinfo=UTC),
            source_type=SourceType.DOCUMENTATION,
        )
        return [RetrievalRow(evidence=evidence, fused_rank=1)]


class FakeExtractor:
    async def extract(
        self, branch: ComparisonRetrievalBranch, *, language: str = "en-US"
    ) -> list[ComparisonObservation]:
        del language
        return [
            ComparisonObservation(
                value="documented",
                unit=None,
                period=None,
                version=None,
                observed_at=branch.rows[0].evidence.captured_at,
                evidence_ids=(branch.rows[0].evidence.id,),
            )
        ]


@pytest.mark.asyncio
async def test_executor_connects_embedding_retrieval_and_workflow() -> None:
    executor = RetrievalComparisonExecutor(
        embedding_provider=FakeEmbeddingProvider(),
        retrieval=ComparisonRetrievalService(FakeRetriever()),
        extractor=FakeExtractor(),
    )
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.CAPABILITY],
    )

    matrix = await executor.run(request, snapshot_id=uuid4(), is_cancelled=lambda: False)

    assert len(matrix.cells) == 2
    assert {cell.value for cell in matrix.cells} == {"documented"}
    assert all(cell.evidence_ids for cell in matrix.cells)
