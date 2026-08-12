from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl

from atlas.comparison.normalization import ComparisonObservation
from atlas.comparison.retrieval import ComparisonRetrievalBranch
from atlas.comparison.schemas import ComparisonCellState, ComparisonCriterion, ComparisonRequest
from atlas.comparison.workflow import ComparisonWorkflow, ComparisonWorkflowCancelled
from atlas.domain import CollectionSlug, Evidence, SourceType
from atlas.retrieval.service import RetrievalRow


def _row(title: str) -> RetrievalRow:
    return RetrievalRow(
        evidence=Evidence(
            id=uuid4(),
            source_title=title,
            publisher="ATLAS test",
            canonical_url=HttpUrl(f"https://example.com/{title}"),
            excerpt="120 ms",
            captured_at=datetime(2026, 8, 5, tzinfo=UTC),
            source_type=SourceType.DOCUMENTATION,
        ),
        fused_rank=1,
    )


class FakeRetrieval:
    async def retrieve(
        self,
        request: ComparisonRequest,
        *,
        snapshot_id: UUID,
        embeddings: dict[ComparisonCriterion, Sequence[float]],
        top_k: int = 8,
    ) -> list[ComparisonRetrievalBranch]:
        del embeddings, top_k
        return [
            ComparisonRetrievalBranch(
                technology=technology,
                criterion=criterion,
                snapshot_id=snapshot_id,
                rows=(_row(f"{technology}-{criterion}"),),
            )
            for technology in request.technologies
            for criterion in request.criteria
        ]


class FakeExtractor:
    async def extract(
        self, branch: ComparisonRetrievalBranch, *, language: str = "en-US"
    ) -> list[ComparisonObservation]:
        del language
        return [
            ComparisonObservation(
                value="120",
                unit="ms",
                period="p95",
                version="1.0",
                observed_at=branch.rows[0].evidence.captured_at,
                evidence_ids=(branch.rows[0].evidence.id,),
            )
        ]


class BoundedExtractor(FakeExtractor):
    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    async def extract(
        self, branch: ComparisonRetrievalBranch, *, language: str = "en-US"
    ) -> list[ComparisonObservation]:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(0)
            return await super().extract(branch, language=language)
        finally:
            self.active -= 1


class CancellingExtractor(FakeExtractor):
    def __init__(self, state: dict[str, bool]) -> None:
        self._state = state

    async def extract(
        self, branch: ComparisonRetrievalBranch, *, language: str = "en-US"
    ) -> list[ComparisonObservation]:
        self._state["cancelled"] = True
        await asyncio.sleep(0)
        return await super().extract(branch, language=language)


class ForeignEvidenceExtractor(FakeExtractor):
    async def extract(
        self, branch: ComparisonRetrievalBranch, *, language: str = "en-US"
    ) -> list[ComparisonObservation]:
        del language
        return [
            ComparisonObservation(
                value="not from this branch",
                unit=None,
                period=None,
                version=None,
                observed_at=None,
                evidence_ids=(uuid4(),),
            )
        ]


@pytest.mark.asyncio
async def test_workflow_fanout_builds_matrix_and_applies_evidence_gate() -> None:
    workflow = ComparisonWorkflow(FakeRetrieval(), FakeExtractor())
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.LATENCY],
    )

    matrix = await workflow.run(
        request,
        snapshot_id=uuid4(),
        embeddings={ComparisonCriterion.LATENCY: [0.1]},
    )

    assert len(matrix.cells) == 2
    assert all(cell.state is ComparisonCellState.SUPPORTED for cell in matrix.cells)
    assert all(cell.evidence_ids for cell in matrix.cells)


@pytest.mark.asyncio
async def test_workflow_stops_before_publishing_when_cancelled() -> None:
    workflow = ComparisonWorkflow(FakeRetrieval(), FakeExtractor())
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.LATENCY],
    )

    with pytest.raises(ComparisonWorkflowCancelled):
        await workflow.run(
            request,
            snapshot_id=uuid4(),
            embeddings={ComparisonCriterion.LATENCY: [0.1]},
            is_cancelled=lambda: True,
        )


@pytest.mark.asyncio
async def test_workflow_extracts_independent_branches_with_bounded_concurrency() -> None:
    extractor = BoundedExtractor()
    workflow = ComparisonWorkflow(FakeRetrieval(), extractor, max_extraction_concurrency=2)
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.CAPABILITY, ComparisonCriterion.CONTEXT],
    )

    matrix = await workflow.run(
        request,
        snapshot_id=uuid4(),
        embeddings={
            ComparisonCriterion.CAPABILITY: [0.1],
            ComparisonCriterion.CONTEXT: [0.2],
        },
    )

    assert len(matrix.cells) == 4
    assert extractor.max_active == 2


@pytest.mark.asyncio
async def test_workflow_propagates_cancellation_from_parallel_branch() -> None:
    state = {"cancelled": False}
    workflow = ComparisonWorkflow(
        FakeRetrieval(),
        CancellingExtractor(state),
        max_extraction_concurrency=4,
    )
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.CAPABILITY, ComparisonCriterion.CONTEXT],
    )

    with pytest.raises(ComparisonWorkflowCancelled):
        await workflow.run(
            request,
            snapshot_id=uuid4(),
            embeddings={
                ComparisonCriterion.CAPABILITY: [0.1],
                ComparisonCriterion.CONTEXT: [0.2],
            },
            is_cancelled=lambda: state["cancelled"],
        )


@pytest.mark.asyncio
async def test_workflow_rejects_evidence_outside_the_retrieved_branch() -> None:
    workflow = ComparisonWorkflow(FakeRetrieval(), ForeignEvidenceExtractor())
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.CAPABILITY],
    )

    with pytest.raises(ValueError, match="outside its retrieval branch"):
        await workflow.run(
            request,
            snapshot_id=uuid4(),
            embeddings={ComparisonCriterion.CAPABILITY: [0.1]},
        )


@pytest.mark.asyncio
async def test_workflow_marks_framework_price_not_applicable_and_writes_conclusion() -> None:
    workflow = ComparisonWorkflow(FakeRetrieval(), FakeExtractor())
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.PRICE],
        language="es-MX",
    )

    matrix = await workflow.run(
        request,
        snapshot_id=uuid4(),
        embeddings={ComparisonCriterion.PRICE: [0.1]},
    )

    langgraph = next(cell for cell in matrix.cells if cell.technology_id is CollectionSlug.LANGGRAPH)
    openai = next(cell for cell in matrix.cells if cell.technology_id is CollectionSlug.OPENAI)
    assert langgraph.state is ComparisonCellState.NOT_APPLICABLE
    assert openai.state is ComparisonCellState.SUPPORTED
    assert matrix.summary and "Conclusión" in matrix.summary
