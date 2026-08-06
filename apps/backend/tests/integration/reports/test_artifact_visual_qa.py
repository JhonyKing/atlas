from io import BytesIO
from zipfile import ZipFile

import pytest
from pypdf import PdfReader

from atlas.reports.planner import plan_report
from atlas.reports.renderers.docx import render_docx
from atlas.reports.renderers.pdf import render_pdf
from atlas.reports.schemas import ReportSpec
from atlas.reports.validation import validate_docx, validate_pdf

from ...unit.reports.test_planner import Source, _completed


@pytest.mark.asyncio
async def test_rendered_artifacts_have_visible_content_on_every_page() -> None:
    source = _completed()
    report = await plan_report(
        ReportSpec(source_run_id=source.run_id, audience="engineer", scope="comparison"),
        owner_key_hash="visitor",
        source=Source(source),
    )
    docx = render_docx(report)
    pdf = render_pdf(report)
    validate_docx(docx, report)
    validate_pdf(pdf, report)
    with ZipFile(BytesIO(docx)) as archive:
        assert "Technology comparison report" in archive.read("word/document.xml").decode()
    pages = PdfReader(BytesIO(pdf)).pages
    assert pages
    assert all((page.extract_text() or "").strip() for page in pages)
