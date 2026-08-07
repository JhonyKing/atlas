from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from atlas.comparison.normalization import ComparisonObservation, normalize_observations
from atlas.comparison.schemas import ComparisonCellState, ComparisonCriterion
from atlas.domain import CollectionSlug


def _observation(
    *,
    evidence_id: UUID | None = None,
    value: str | None = "120",
    unit: str | None = "ms",
    period: str | None = None,
    version: str | None = "1.0",
) -> ComparisonObservation:
    return ComparisonObservation(
        value=value,
        unit=unit,
        period=period,
        version=version,
        observed_at=datetime(2026, 8, 5, tzinfo=UTC),
        evidence_ids=(evidence_id or uuid4(),),
    )


def test_normalization_preserves_unit_period_version_and_evidence() -> None:
    evidence_id = uuid4()
    cell = normalize_observations(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.LATENCY,
        observations=[_observation(evidence_id=evidence_id, period="p95")],
    )

    assert cell.state is ComparisonCellState.SUPPORTED
    assert cell.value == "120"
    assert cell.unit == "ms"
    assert cell.period == "p95"
    assert cell.version == "1.0"
    assert cell.evidence_ids == [evidence_id]


def test_normalization_marks_missing_values_unsupported() -> None:
    cell = normalize_observations(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.PRICE,
        observations=[_observation(value=None, unit="USD")],
    )

    assert cell.state is ComparisonCellState.UNSUPPORTED
    assert cell.value is None
    assert cell.evidence_ids == []
    assert cell.explanation


def test_normalization_marks_incompatible_units_contradictory() -> None:
    first = _observation(value="120", unit="ms")
    second = _observation(value="2", unit="seconds")
    cell = normalize_observations(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.LATENCY,
        observations=[first, second],
    )

    assert cell.state is ComparisonCellState.CONTRADICTORY
    assert cell.value is None
    assert len(cell.evidence_ids) == 2
    assert "unit" in (cell.explanation or "").lower()


def test_normalization_marks_same_unit_different_values_partial() -> None:
    cell = normalize_observations(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CONTEXT,
        observations=[_observation(value="8k"), _observation(value="16k")],
    )

    assert cell.state is ComparisonCellState.PARTIAL
    assert cell.value is None
    assert "different" in (cell.explanation or "").lower()
