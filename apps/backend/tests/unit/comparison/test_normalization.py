from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from atlas.comparison.normalization import (
    ComparisonObservation,
    ComparisonObservationRelation,
    normalize_observations,
)
from atlas.comparison.schemas import ComparisonCellState, ComparisonCriterion
from atlas.domain import CollectionSlug


def _observation(
    *,
    evidence_id: UUID | None = None,
    value: str | None = "120",
    unit: str | None = "ms",
    period: str | None = None,
    version: str | None = "1.0",
    relation: ComparisonObservationRelation = ComparisonObservationRelation.UNKNOWN,
) -> ComparisonObservation:
    return ComparisonObservation(
        value=value,
        unit=unit,
        period=period,
        version=version,
        observed_at=datetime(2026, 8, 5, tzinfo=UTC),
        evidence_ids=(evidence_id or uuid4(),),
        relation=relation,
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


def test_normalization_can_mark_framework_price_as_not_applicable() -> None:
    cell = normalize_observations(
        technology_id=CollectionSlug.LANGGRAPH,
        criterion_id=ComparisonCriterion.PRICE,
        observations=[],
        not_applicable=True,
        language="es-MX",
    )

    assert cell.state is ComparisonCellState.NOT_APPLICABLE
    assert cell.evidence_ids == []
    assert "no aplica" in (cell.explanation or "").lower()


def test_normalization_localizes_explanation_without_changing_value() -> None:
    cell = normalize_observations(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CONTEXT,
        observations=[_observation(value="8k"), _observation(value="16k")],
        language="es-MX",
    )

    assert cell.value is None
    assert "valores diferentes" in (cell.explanation or "").lower()
    assert "different values" not in (cell.explanation or "").lower()


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


def test_normalization_preserves_complementary_qualitative_observations() -> None:
    cell = normalize_observations(
        technology_id=CollectionSlug.LANGGRAPH,
        criterion_id=ComparisonCriterion.CAPABILITY,
        observations=[
            _observation(
                value="supports persistence",
                unit=None,
                relation=ComparisonObservationRelation.SUPPORTS,
            ),
            _observation(
                value="supports streaming",
                unit=None,
                relation=ComparisonObservationRelation.COMPLEMENTS,
            ),
        ],
    )

    assert cell.state is ComparisonCellState.PARTIAL
    assert cell.value == "supports persistence; supports streaming"
    assert "qualitative" in (cell.explanation or "").lower()
    assert "different values" not in (cell.explanation or "").lower()


def test_normalization_merges_qualitative_claims_without_relation_metadata() -> None:
    cell = normalize_observations(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CAPABILITY,
        observations=[
            _observation(value="browser", unit=None),
            _observation(value="web search", unit=None),
        ],
    )

    assert cell.state is ComparisonCellState.PARTIAL
    assert cell.value == "browser; web search"
    assert "qualitative" in (cell.explanation or "").lower()


def test_normalization_marks_explicitly_contradictory_observations() -> None:
    cell = normalize_observations(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CAPABILITY,
        observations=[
            _observation(value="available", relation=ComparisonObservationRelation.SUPPORTS),
            _observation(
                value="unavailable", relation=ComparisonObservationRelation.CONTRADICTS
            ),
        ],
    )

    assert cell.state is ComparisonCellState.CONTRADICTORY
    assert cell.value is None
    assert "contradict" in (cell.explanation or "").lower()
