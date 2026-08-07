from pathlib import Path

import pytest

from atlas.reports.planner import plan_report
from atlas.reports.renderers.docx import render_docx
from atlas.reports.renderers.pdf import render_pdf
from atlas.reports.schemas import ReportSpec
from atlas.reports.validation import validate_docx, validate_pdf

from .test_planner import Source, _completed


@pytest.mark.asyncio
async def test_docx_and_pdf_are_non_empty_and_citation_complete(
    tmp_path: Path,
) -> None:
    source = _completed()
    report = await plan_report(
        ReportSpec(source_run_id=source.run_id, audience="engineer", scope="comparison"),
        owner_key_hash="visitor",
        source=Source(source),
    )
    docx = render_docx(report)
    pdf = render_pdf(report)
    (tmp_path / "report.docx").write_bytes(docx)
    (tmp_path / "report.pdf").write_bytes(pdf)
    validate_docx(docx, report)
    validate_pdf(pdf, report)
    assert len(docx) > 100
    assert len(pdf) > 100
