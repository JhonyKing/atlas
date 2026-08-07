from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from atlas.api.routes.comparisons import ComparisonRunResponse
from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
)
from atlas.domain import CollectionSlug
from atlas.reports.planner import ReportPlanningError, plan_report
from atlas.reports.schemas import ReportLocale, ReportSpec


class Source:
    def __init__(self, response: ComparisonRunResponse | None) -> None:
        self.response = response

    async def get_status(
        self, run_id: UUID, *, visitor_key_hash: str
    ) -> ComparisonRunResponse | None:
        del run_id, visitor_key_hash
        return self.response


def _completed() -> ComparisonRunResponse:
    run_id = uuid4()
    evidence_id = uuid4()
    matrix = ComparisonMatrix(
        technology_ids=[CollectionSlug("openai"), CollectionSlug("anthropic")],
        criterion_ids=[ComparisonCriterion.CAPABILITY],
        cells=[
            ComparisonCell(
                technology_id=CollectionSlug("openai"),
                criterion_id=ComparisonCriterion.CAPABILITY,
                state=ComparisonCellState.SUPPORTED,
                value="yes",
                evidence_ids=[evidence_id],
            ),
            ComparisonCell(
                technology_id=CollectionSlug("anthropic"),
                criterion_id=ComparisonCriterion.CAPABILITY,
                state=ComparisonCellState.SUPPORTED,
                value="yes",
                evidence_ids=[evidence_id],
            ),
        ],
        summary="Verified comparison",
    )
    return ComparisonRunResponse(
        run_id=run_id,
        status="completed",
        created_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        matrix=matrix,
        retained_until=datetime.now(UTC) + timedelta(days=30),
    )


@pytest.mark.asyncio
async def test_planner_preserves_evidence_identity_and_localizes_headings() -> None:
    source = _completed()
    spec = ReportSpec(
        source_run_id=source.run_id,
        audience="engineer",
        scope="comparison",
        locale=ReportLocale.ES_MX,
    )
    report = await plan_report(spec, owner_key_hash="visitor", source=Source(source))
    assert source.matrix is not None
    assert report.locale is ReportLocale.ES_MX
    assert report.citations[0].evidence_id in {cell.evidence_ids[0] for cell in source.matrix.cells}
    assert report.sections[0].title == "Resumen ejecutivo"


@pytest.mark.asyncio
async def test_planner_fails_closed_for_missing_source() -> None:
    spec = ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison")
    with pytest.raises(ReportPlanningError, match="source_run_not_found"):
        await plan_report(spec, owner_key_hash="visitor", source=Source(None))


@pytest.mark.asyncio
async def test_planner_fails_closed_for_completed_run_without_evidence() -> None:
    source = Source(_completed())
    assert source.response is not None
    matrix = source.response.matrix
    assert matrix is not None
    cells = [
        cell.model_copy(
            update={
                "state": ComparisonCellState.UNSUPPORTED,
                "evidence_ids": [],
                "value": None,
                "explanation": "No evidence",
            }
        )
        for cell in matrix.cells
    ]
    assert source.response is not None
    source.response = source.response.model_copy(
        update={"matrix": matrix.model_copy(update={"cells": cells})}
    )
    spec = ReportSpec(source_run_id=source.response.run_id, audience="engineer", scope="comparison")
    with pytest.raises(ReportPlanningError, match="source_run_has_no_evidence"):
        await plan_report(spec, owner_key_hash="visitor", source=source)
