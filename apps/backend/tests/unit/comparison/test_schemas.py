from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
    ComparisonRequest,
    ComparisonRun,
    ComparisonRunStatus,
)
from atlas.domain import CollectionSlug


def test_request_accepts_two_to_four_unique_technologies_and_criteria() -> None:
    request = ComparisonRequest(
        technologies=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
        criteria=[ComparisonCriterion.CAPABILITY, ComparisonCriterion.PRICE],
        language="es-MX",
    )

    assert request.technologies == [CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI]
    assert request.language == "es-MX"


@pytest.mark.parametrize(
    "technologies",
    [[], [CollectionSlug.OPENAI], [CollectionSlug.OPENAI] * 2, list(CollectionSlug) * 2],
)
def test_request_rejects_invalid_technology_selection(technologies: list[CollectionSlug]) -> None:
    with pytest.raises(ValidationError):
        ComparisonRequest(technologies=technologies, criteria=[ComparisonCriterion.CAPABILITY])


def test_cell_requires_evidence_for_supported_values_and_explanation_for_gaps() -> None:
    evidence_id = uuid4()
    supported = ComparisonCell(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CAPABILITY,
        state=ComparisonCellState.SUPPORTED,
        value="Structured outputs",
        evidence_ids=[evidence_id],
    )
    assert supported.evidence_ids == [evidence_id]

    with pytest.raises(ValidationError):
        ComparisonCell(
            technology_id=CollectionSlug.OPENAI,
            criterion_id=ComparisonCriterion.CAPABILITY,
            state=ComparisonCellState.SUPPORTED,
            value="Structured outputs",
            evidence_ids=[],
        )
    with pytest.raises(ValidationError):
        ComparisonCell(
            technology_id=CollectionSlug.OPENAI,
            criterion_id=ComparisonCriterion.CAPABILITY,
            state=ComparisonCellState.UNSUPPORTED,
            evidence_ids=[],
        )


def test_matrix_rejects_duplicate_coordinates_and_wrong_cell_count() -> None:
    cell = ComparisonCell(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CAPABILITY,
        state=ComparisonCellState.UNSUPPORTED,
        explanation="No supporting source was captured.",
        evidence_ids=[],
    )
    with pytest.raises(ValidationError):
        ComparisonMatrix(
            technology_ids=[CollectionSlug.OPENAI],
            criterion_ids=[ComparisonCriterion.CAPABILITY],
            cells=[cell, cell],
        )


def test_cell_dates_are_utc_aware_when_present() -> None:
    cell = ComparisonCell(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.FRESHNESS,
        state=ComparisonCellState.PARTIAL,
        value="Current as of capture",
        explanation="The source provides capture date but no release date.",
        evidence_ids=[uuid4()],
        observed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    assert cell.observed_at is not None and cell.observed_at.tzinfo is not None


def test_comparison_run_has_stable_identity_and_terminal_status() -> None:
    run_id = uuid4()
    run = ComparisonRun(
        run_id=run_id,
        request_id=uuid4(),
        visitor_key_hash="hmac:visitor",
        snapshot_id=uuid4(),
        status=ComparisonRunStatus.ACCEPTED,
        created_at=datetime(2026, 8, 5, tzinfo=UTC),
        completed_at=None,
        retained_until=datetime(2026, 9, 4, tzinfo=UTC),
    )

    assert run.run_id == run_id
    assert run.status is ComparisonRunStatus.ACCEPTED

    with pytest.raises(ValidationError):
        ComparisonRun(
            run_id=run_id,
            request_id=uuid4(),
            visitor_key_hash="hmac:visitor",
            snapshot_id=uuid4(),
            status=ComparisonRunStatus.COMPLETED,
            created_at=datetime(2026, 8, 5, tzinfo=UTC),
            completed_at=None,
            retained_until=datetime(2026, 9, 4, tzinfo=UTC),
        )
