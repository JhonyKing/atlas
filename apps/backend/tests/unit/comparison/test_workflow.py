from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

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
            canonical_url=f"https://example.com/{title}",
            excerpt="120 ms",
            captured_at=datetime(2026, 8, 5, tzinfo=UTC),
            source_type=SourceType.DOCUMENTATION,
        ),
        fused_rank=1,
    )


class FakeRetrieval:
    async def retrieve(self, request, *, snapshot_id, embeddings, top_k=8):
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
    async def extract(self, branch: ComparisonRetrievalBranch) -> list[ComparisonObservation]:
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
