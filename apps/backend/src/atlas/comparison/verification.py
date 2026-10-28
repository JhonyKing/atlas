"""Final evidence gate for comparison matrices."""

from __future__ import annotations

from atlas.comparison.schemas import ComparisonCellState, ComparisonMatrix


class ComparisonVerificationError(ValueError):
    """The matrix cannot be published as verified."""


def verify_matrix(matrix: ComparisonMatrix) -> ComparisonMatrix:
    for cell in matrix.cells:
        if cell.state in {
            ComparisonCellState.UNSUPPORTED,
            ComparisonCellState.NOT_APPLICABLE,
        }:
            if cell.evidence_ids:
                raise ComparisonVerificationError(
                    "unsupported and not-applicable cells cannot contain evidence"
                )
            if not cell.explanation:
                raise ComparisonVerificationError("unsupported cells require an explanation")
            continue
        if not cell.evidence_ids:
            raise ComparisonVerificationError("populated cells require evidence")
        if (
            cell.state
            in {
                ComparisonCellState.PARTIAL,
                ComparisonCellState.CONTRADICTORY,
            }
            and not cell.explanation
        ):
            raise ComparisonVerificationError(
                "partial and contradictory cells require an explanation"
            )
    return matrix
