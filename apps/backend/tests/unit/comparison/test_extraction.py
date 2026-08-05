from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from atlas.comparison.extraction import (
    ComparisonExtraction,
    ComparisonObservationItem,
    validate_extraction,
)


def test_extraction_rejects_evidence_outside_retrieved_branch() -> None:
    allowed = uuid4()
    with pytest.raises(ValueError, match="outside the retrieved branch"):
        validate_extraction(
            ComparisonExtraction(
                observations=[ComparisonObservationItem(value="yes", evidence_ids=[uuid4()])]
            ),
            allowed_evidence_ids=[allowed],
        )


def test_extraction_preserves_explicit_context_and_deduplicates_ids() -> None:
    evidence_id = UUID("00000000-0000-0000-0000-000000000101")
    result = validate_extraction(
        ComparisonExtraction(
            observations=[
                ComparisonObservationItem(
                    value="128k",
                    unit="tokens",
                    period="2026-Q1",
                    version="v1",
                    observed_at=datetime(2026, 8, 5, tzinfo=UTC),
                    evidence_ids=[evidence_id, evidence_id],
                )
            ]
        ),
        allowed_evidence_ids=[evidence_id],
    )
    assert result[0].value == "128k"
    assert result[0].unit == "tokens"
    assert result[0].evidence_ids == (evidence_id,)


def test_extraction_schema_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ComparisonExtraction.model_validate({"observations": [], "action": "delete"})
