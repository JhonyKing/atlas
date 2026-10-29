from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from pypdf import PdfReader

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
    with ZipFile(BytesIO(docx)) as archive:
        assert "word/media/image1.png" in archive.namelist()
        relationships = archive.read("word/_rels/document.xml.rels").decode()
        assert "https://example.com/docs" in relationships
        footer_relationships = archive.read("word/_rels/footer1.xml.rels").decode()
        assert "https://atlasai-lilac.vercel.app" in footer_relationships
    reader = PdfReader(BytesIO(pdf))
    pdf_links = {
        annotation.get_object().get("/A", {}).get("/URI")
        for page in reader.pages
        for annotation in page.get("/Annots", [])
    }
    assert "https://example.com/docs" in pdf_links
    assert "https://atlasai-lilac.vercel.app" in pdf_links
