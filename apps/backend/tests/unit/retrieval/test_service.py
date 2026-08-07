from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl

from atlas.domain import CollectionSlug, Evidence, Question, SourceType
from atlas.retrieval.query import RetrievalFilters
from atlas.retrieval.service import RetrievalRow, RetrievalService


def evidence(*, evidence_id: UUID, title: str) -> Evidence:
    return Evidence(
        id=evidence_id,
        source_title=title,
        publisher="Official publisher",
        canonical_url=HttpUrl("https://docs.example.test/reference"),
        excerpt=f"Supporting excerpt for {title}.",
        captured_at=datetime(2026, 8, 4, tzinfo=UTC),
        version_label="1.0",
        source_type=SourceType.DOCUMENTATION,
    )


class FakeRetrievalRepository:
    def __init__(self, rows: list[RetrievalRow]) -> None:
        self.rows = rows
        self.snapshot_calls: list[CollectionSlug | None] = []
        self.search_calls: list[dict[str, object]] = []

    async def select_snapshot(self, collection: CollectionSlug | None) -> UUID:
        self.snapshot_calls.append(collection)
        return UUID("00000000-0000-0000-0000-000000000123")

    async def search(
        self,
        *,
        collection: CollectionSlug | None,
        query_text: str,
        embedding: list[float],
        top_k: int,
        snapshot_id: UUID,
        version: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> list[RetrievalRow]:
        self.search_calls.append(
            {
                "collection": collection,
                "query_text": query_text,
                "embedding": embedding,
                "top_k": top_k,
                "snapshot_id": snapshot_id,
                "version": version,
                "date_from": date_from,
                "date_to": date_to,
            }
        )
        return self.rows


@pytest.mark.asyncio
async def test_retrieval_preserves_constraints_selects_snapshot_and_orders_deterministically(
) -> None:
    first_id = UUID("00000000-0000-0000-0000-000000000001")
    second_id = UUID("00000000-0000-0000-0000-000000000002")
    repository = FakeRetrievalRepository(
        [
            RetrievalRow(evidence=evidence(evidence_id=second_id, title="Second"), fused_rank=2),
            RetrievalRow(evidence=evidence(evidence_id=first_id, title="First"), fused_rank=1),
            RetrievalRow(evidence=evidence(evidence_id=first_id, title="Duplicate"), fused_rank=3),
        ]
    )
    service = RetrievalService(repository)
    question = Question(
        text="  How does LangGraph work? ",
        product=CollectionSlug.LANGGRAPH,
        version="1.0",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 8, 4),
    )

    results = await service.retrieve(question, [0.0, 1.0], top_k=8)

    assert [row.evidence.id for row in results] == [first_id, second_id]
    assert repository.snapshot_calls == [CollectionSlug.LANGGRAPH]
    assert repository.search_calls == [
        {
            "collection": CollectionSlug.LANGGRAPH,
            "query_text": "how does langgraph work?",
            "embedding": [0.0, 1.0],
            "top_k": 8,
            "snapshot_id": UUID("00000000-0000-0000-0000-000000000123"),
            "version": "1.0",
            "date_from": date(2026, 1, 1),
            "date_to": date(2026, 8, 4),
        }
    ]


@pytest.mark.asyncio
async def test_retrieval_rejects_unbounded_top_k_before_querying() -> None:
    repository = FakeRetrievalRepository([])
    service = RetrievalService(repository)
    question = Question(text="What is LangGraph?", product=CollectionSlug.LANGGRAPH)

    with pytest.raises(ValueError, match="top_k"):
        await service.retrieve(question, [0.0], top_k=0)
    with pytest.raises(ValueError, match="top_k"):
        await service.retrieve(question, [0.0], top_k=51)
    assert repository.search_calls == []


@pytest.mark.asyncio
async def test_retrieval_uses_explicit_snapshot_without_reselecting_latest() -> None:
    repository = FakeRetrievalRepository([])
    service = RetrievalService(repository)
    question = Question(text="What is LangGraph?", product=None)
    snapshot_id = uuid4()

    await service.retrieve(question, [0.0], snapshot_id=snapshot_id, top_k=1)

    assert repository.snapshot_calls == []
    assert repository.search_calls[0]["collection"] is None
    assert repository.search_calls[0]["snapshot_id"] == snapshot_id


@pytest.mark.asyncio
async def test_retrieval_records_bounded_rewrite_and_applies_available_filters() -> None:
    first_id = UUID("00000000-0000-0000-0000-000000000011")
    second_id = UUID("00000000-0000-0000-0000-000000000012")
    repository = FakeRetrievalRepository(
        [
            RetrievalRow(evidence=evidence(evidence_id=first_id, title="StateGraph"), fused_rank=1),
            RetrievalRow(evidence=evidence(evidence_id=second_id, title="Other"), fused_rank=2),
        ]
    )
    service = RetrievalService(repository, aliases={"langgraph": ("StateGraph",)})
    question = Question(text="What is LangGraph?", product=CollectionSlug.LANGGRAPH)

    results = await service.retrieve(
        question,
        [0.0],
        filters=RetrievalFilters(
            collection=CollectionSlug.LANGGRAPH,
            source_type=SourceType.DOCUMENTATION,
        ),
    )

    assert [row.evidence.id for row in results] == [first_id, second_id]
    assert repository.search_calls[0]["query_text"] == "what is langgraph? StateGraph"
    assert service.last_metadata["rewritten_terms"] == ("StateGraph",)


@pytest.mark.asyncio
async def test_retrieval_enforces_all_filter_dimensions_before_ranking() -> None:
    matching_id = UUID("00000000-0000-0000-0000-000000000021")
    rejected_id = UUID("00000000-0000-0000-0000-000000000022")
    matching = evidence(evidence_id=matching_id, title="LangGraph OpenAI")
    rejected = evidence(evidence_id=rejected_id, title="LangGraph OpenAI")
    rejected = rejected.model_copy(
        update={"version_label": "0.9", "source_type": SourceType.CHANGELOG}
    )
    repository = FakeRetrievalRepository(
        [
            RetrievalRow(evidence=rejected, fused_rank=1),
            RetrievalRow(evidence=matching, fused_rank=2),
        ]
    )
    service = RetrievalService(repository)
    question = Question(text="OpenAI LangGraph version", product=CollectionSlug.OPENAI)

    results = await service.retrieve(
        question,
        [0.0],
        filters=RetrievalFilters(
            provider="openai",
            framework="langgraph",
            version="1.0",
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 5),
            language="en-US",
            source_type=SourceType.DOCUMENTATION,
            collection=CollectionSlug.OPENAI,
        ),
    )

    assert [row.evidence.id for row in results] == [matching_id]
