"""Deterministic normalization of comparison observations into explicit cell states."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from atlas.comparison.schemas import ComparisonCell, ComparisonCellState, ComparisonCriterion
from atlas.domain import CollectionSlug


class ComparisonObservationRelation(StrEnum):
    """How an extracted observation relates to the other observations in its cell."""

    UNKNOWN = "unknown"
    SUPPORTS = "supports"
    COMPLEMENTS = "complements"
    CONTRADICTS = "contradicts"


@dataclass(frozen=True, slots=True)
class ComparisonObservation:
    value: str | None
    unit: str | None
    period: str | None
    version: str | None
    observed_at: datetime | None
    evidence_ids: tuple[UUID, ...]
    relation: ComparisonObservationRelation = ComparisonObservationRelation.UNKNOWN


def normalize_observations(
    *,
    technology_id: CollectionSlug,
    criterion_id: ComparisonCriterion,
    observations: list[ComparisonObservation],
    language: Literal["en-US", "es-MX"] = "en-US",
    not_applicable: bool = False,
) -> ComparisonCell:
    evidence_ids = _unique_evidence_ids(observations)
    if not_applicable:
        return ComparisonCell(
            technology_id=technology_id,
            criterion_id=criterion_id,
            state=ComparisonCellState.NOT_APPLICABLE,
            explanation=_message(
                language,
                en="This criterion does not apply to the selected product type.",
                es="Este criterio no aplica al tipo de producto seleccionado.",
            ),
            evidence_ids=[],
        )
    populated = [observation for observation in observations if observation.value is not None]
    if not populated:
        return ComparisonCell(
            technology_id=technology_id,
            criterion_id=criterion_id,
            state=ComparisonCellState.UNSUPPORTED,
            explanation=_message(
                language,
                en="No comparable value was found in the selected evidence.",
                es="No se encontró un valor comparable en la evidencia seleccionada.",
            ),
            evidence_ids=[],
        )

    if any(
        observation.relation is ComparisonObservationRelation.CONTRADICTS
        for observation in populated
    ):
        return _contradictory(
            technology_id,
            criterion_id,
            evidence_ids,
            _message(
                language,
                en="Sources explicitly contradict one another for this comparison criterion.",
                es="Las fuentes se contradicen explícitamente para este criterio de comparación.",
            ),
        )

    units = {observation.unit for observation in populated}
    if len(units) > 1:
        return _contradictory(
            technology_id,
            criterion_id,
            evidence_ids,
            _message(
                language,
                en="Sources use incompatible units; ATLAS does not infer a conversion.",
                es="Las fuentes usan unidades incompatibles; ATLAS no infiere conversiones.",
            ),
        )

    values = {observation.value for observation in populated}
    unit = next(iter(units))
    first = populated[0]
    if len(values) > 1:
        if _is_qualitative_observation_set(populated, unit=unit):
            return ComparisonCell(
                technology_id=technology_id,
                criterion_id=criterion_id,
                state=ComparisonCellState.PARTIAL,
                value=_combine_values(populated),
                unit=unit,
                explanation=(
                    _message(
                        language,
                        en=(
                            "Sources provide multiple qualitative observations without an explicit "
                            "direct contradiction; the comparison preserves each fact."
                        ),
                        es=(
                            "Las fuentes aportan varias observaciones cualitativas sin una "
                            "contradicción directa; la comparación conserva cada hecho."
                        ),
                    )
                ),
                evidence_ids=evidence_ids,
                period=first.period,
                version=first.version,
                observed_at=first.observed_at,
            )
        return ComparisonCell(
            technology_id=technology_id,
            criterion_id=criterion_id,
            state=ComparisonCellState.PARTIAL,
            unit=unit,
            explanation=(
                _message(
                    language,
                    en=(
                        "Sources report different values; the comparison preserves the "
                        "disagreement."
                    ),
                    es=(
                        "Las fuentes reportan valores diferentes; la comparación conserva la "
                        "discrepancia."
                    ),
                )
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


def _combine_values(observations: list[ComparisonObservation]) -> str:
    values = list(
        dict.fromkeys(observation.value for observation in observations if observation.value)
    )
    combined = "; ".join(values)
    return combined if len(combined) <= 2000 else f"{combined[:1997]}..."


def _is_qualitative_observation_set(
    observations: list[ComparisonObservation], *, unit: str | None
) -> bool:
    """Identify prose claims that can be preserved instead of treated as scalar conflict."""

    if unit is not None:
        return False
    values = [observation.value or "" for observation in observations]
    return all(
        " " in value or not any(character.isdigit() for character in value)
        for value in values
    )


def _message(language: Literal["en-US", "es-MX"], *, en: str, es: str) -> str:
    return es if language == "es-MX" else en
