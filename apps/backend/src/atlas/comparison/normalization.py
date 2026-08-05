"""Deterministic normalization of comparison observations into explicit cell states."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from atlas.comparison.schemas import ComparisonCell, ComparisonCellState, ComparisonCriterion
from atlas.domain import CollectionSlug


@dataclass(frozen=True, slots=True)
class ComparisonObservation:
    value: str | None
    unit: str | None
    period: str | None
    version: str | None
    observed_at: datetime | None
    evidence_ids: tuple[UUID, ...]


def normalize_observations(
    *,
    technology_id: CollectionSlug,
    criterion_id: ComparisonCriterion,
    observations: list[ComparisonObservation],
) -> ComparisonCell:
    evidence_ids = _unique_evidence_ids(observations)
    populated = [observation for observation in observations if observation.value is not None]
    if not populated:
        return ComparisonCell(
            technology_id=technology_id,
            criterion_id=criterion_id,
            state=ComparisonCellState.UNSUPPORTED,
            explanation="No comparable value was found in the selected evidence.",
            evidence_ids=[],
        )

    units = {observation.unit for observation in populated}
    if len(units) > 1:
        return _contradictory(
            technology_id,
            criterion_id,
            evidence_ids,
            "Sources use incompatible units; ATLAS does not infer a conversion.",
        )

    values = {observation.value for observation in populated}
    unit = next(iter(units))
    first = populated[0]
    if len(values) > 1:
        return ComparisonCell(
            technology_id=technology_id,
            criterion_id=criterion_id,
            state=ComparisonCellState.PARTIAL,
            unit=unit,
            explanation=(
                "Sources report different values; the comparison preserves the disagreement."
            ),
            evidence_ids=evidence_ids,
            period=first.period,
            version=first.version,
            observed_at=first.observed_at,
        )

    return ComparisonCell(
        technology_id=technology_id,
        criterion_id=criterion_id,
        state=ComparisonCellState.SUPPORTED,
        value=first.value,
        unit=unit,
        evidence_ids=evidence_ids,
        period=first.period,
        version=first.version,
        observed_at=first.observed_at,
    )


def _contradictory(
    technology_id: CollectionSlug,
    criterion_id: ComparisonCriterion,
    evidence_ids: list[UUID],
    explanation: str,
) -> ComparisonCell:
    return ComparisonCell(
        technology_id=technology_id,
        criterion_id=criterion_id,
        state=ComparisonCellState.CONTRADICTORY,
        explanation=explanation,
        evidence_ids=evidence_ids,
    )


def _unique_evidence_ids(observations: list[ComparisonObservation]) -> list[UUID]:
    result: list[UUID] = []
    seen: set[UUID] = set()
    for observation in observations:
        for evidence_id in observation.evidence_ids:
            if evidence_id not in seen:
                seen.add(evidence_id)
                result.append(evidence_id)
    return result
