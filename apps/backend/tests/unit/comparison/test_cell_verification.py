from __future__ import annotations

from uuid import uuid4

import pytest

from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
)
from atlas.comparison.verification import ComparisonVerificationError, verify_matrix
from atlas.domain import CollectionSlug


def _cell(
    state: ComparisonCellState, *, evidence: bool = True, explanation: str | None = "Reason"
) -> ComparisonCell:
    return ComparisonCell(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CAPABILITY,
        state=state,
        value="Available" if state is ComparisonCellState.SUPPORTED else None,
        explanation=explanation,
        evidence_ids=[uuid4()] if evidence else [],
    )


def test_verification_accepts_explicit_supported_unsupported_partial_and_contradictory_states() -> (
    None
):
    cells = [
        _cell(ComparisonCellState.SUPPORTED),
        _cell(ComparisonCellState.UNSUPPORTED, evidence=False),
        _cell(ComparisonCellState.PARTIAL),
        _cell(ComparisonCellState.CONTRADICTORY),
    ]
    cells[1] = cells[1].model_copy(update={"technology_id": CollectionSlug.LANGGRAPH})
    cells[2] = cells[2].model_copy(update={"technology_id": CollectionSlug.LANGCHAIN})
    matrix = ComparisonMatrix(
        technology_ids=[CollectionSlug.OPENAI, CollectionSlug.LANGGRAPH, CollectionSlug.LANGCHAIN],
        criterion_ids=[ComparisonCriterion.CAPABILITY],
        cells=cells[:3],
    )

    verified = verify_matrix(matrix)

    assert verified == matrix


def test_verification_rejects_populated_cells_without_evidence_or_explanation() -> None:
    invalid_supported = ComparisonCell.model_construct(
        technology_id=CollectionSlug.OPENAI,
        criterion_id=ComparisonCriterion.CAPABILITY,
        state=ComparisonCellState.SUPPORTED,
        value="Available",
        explanation="Reason",
        evidence_ids=[],
    )
    with pytest.raises(ComparisonVerificationError, match="evidence"):
        verify_matrix(
            ComparisonMatrix.model_construct(
                technology_ids=[CollectionSlug.OPENAI, CollectionSlug.LANGGRAPH],
                criterion_ids=[ComparisonCriterion.CAPABILITY],
                cells=[invalid_supported, _cell(ComparisonCellState.UNSUPPORTED, evidence=False)],
            )
        )

    invalid_unsupported = ComparisonCell.model_construct(
        technology_id=CollectionSlug.LANGGRAPH,
        criterion_id=ComparisonCriterion.CAPABILITY,
        state=ComparisonCellState.UNSUPPORTED,
        value=None,
        explanation=None,
        evidence_ids=[],
    )
    with pytest.raises(ComparisonVerificationError, match="explanation"):
        verify_matrix(
            ComparisonMatrix.model_construct(
                technology_ids=[CollectionSlug.OPENAI, CollectionSlug.LANGGRAPH],
                criterion_ids=[ComparisonCriterion.CAPABILITY],
                cells=[
                    _cell(ComparisonCellState.SUPPORTED),
                    invalid_unsupported,
                ],
            )
        )
