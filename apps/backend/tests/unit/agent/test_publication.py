from uuid import uuid4

import pytest

from atlas.agent.publication import PublicationValidationError, validate_report_spec_for_publication


def test_report_publication_uses_existing_typed_report_spec_contract() -> None:
    spec = validate_report_spec_for_publication(
        {
            "source_run_id": uuid4(),
            "audience": "engineer",
            "scope": "comparison",
        }
    )
    assert spec.audience == "engineer"


def test_invalid_report_spec_is_rejected_before_publication() -> None:
    with pytest.raises(PublicationValidationError):
        validate_report_spec_for_publication({"audience": "engineer"})
