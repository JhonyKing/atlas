"""Deterministic evaluators for comparison matrix shape and evidence parity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ComparisonEvaluation:
    case_id: str
    passed: bool
    structure_correct: bool
    state_correct: bool
    evidence_parity: bool
    reasons: tuple[str, ...]


def evaluate_comparison_case(
    case: dict[str, Any], actual: dict[str, Any]
) -> ComparisonEvaluation:
    expected_cells = case.get("expected_cells", [])
    actual_cells = actual.get("cells", actual.get("matrix", {}).get("cells", []))
    expected_coordinates = {
        (cell.get("technology_id"), cell.get("criterion_id")) for cell in expected_cells
    }
    actual_coordinates = {
        (cell.get("technology_id"), cell.get("criterion_id")) for cell in actual_cells
    }
    structure_correct = expected_coordinates == actual_coordinates
    expected_by_coordinate = {
        (cell.get("technology_id"), cell.get("criterion_id")): cell
        for cell in expected_cells
    }
    actual_by_coordinate = {
        (cell.get("technology_id"), cell.get("criterion_id")): cell
        for cell in actual_cells
    }
    state_correct = all(
        actual_by_coordinate.get(coordinate, {}).get("state") == expected.get("state")
        for coordinate, expected in expected_by_coordinate.items()
    )
    evidence_parity = all(
        actual_by_coordinate.get(coordinate, {}).get("evidence_ids", [])
        == expected.get("evidence_ids", [])
        for coordinate, expected in expected_by_coordinate.items()
    )
    reasons: list[str] = []
    if not structure_correct:
        reasons.append("matrix coordinates differ")
    if not state_correct:
        reasons.append("cell states differ")
    if not evidence_parity:
        reasons.append("evidence IDs differ")
    return ComparisonEvaluation(
        case_id=str(case["id"]),
        passed=structure_correct and state_correct and evidence_parity,
        structure_correct=structure_correct,
        state_correct=state_correct,
        evidence_parity=evidence_parity,
        reasons=tuple(reasons),
    )
