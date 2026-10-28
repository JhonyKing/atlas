from uuid import uuid4

import pytest
from pydantic import ValidationError

from atlas.reports.schemas import ReportSpec, ReportType
from atlas.reports.service import _report_spec_from_json


def test_report_spec_defaults_to_comparison_and_docx() -> None:
    spec = ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison")
    assert spec.report_type is ReportType.COMPARISON
    assert spec.format.value == "docx"


def test_stored_json_report_spec_round_trips_strict_enum_values() -> None:
    spec = ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison")

    restored = _report_spec_from_json(spec.model_dump(mode="json"))

    assert restored == spec


def test_report_spec_rejects_duplicate_required_sections() -> None:
    with pytest.raises(ValidationError):
        ReportSpec(
            source_run_id=uuid4(),
            audience="engineer",
            scope="comparison",
            required_sections=["References", "References"],
        )

