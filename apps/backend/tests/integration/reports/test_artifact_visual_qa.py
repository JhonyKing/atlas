import hashlib
import json
from datetime import UTC, datetime
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

    repository_root = Path(__file__).resolve().parents[5]
    evidence_dir = repository_root / "evals" / "results" / "003-reports-artifacts"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = evidence_dir / "comparison-report-en-US.pdf"
    docx_path = evidence_dir / "comparison-report-en-US.docx"
    manifest_path = evidence_dir / "manifest.json"
    pdf_path.write_bytes(pdf)
    docx_path.write_bytes(docx)
    manifest_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "source_run_id": str(source.run_id),
                "report_format": "comparison",
                "locale": "en-US",
                "artifacts": {
                    "pdf": {
                        "path": str(pdf_path.relative_to(repository_root)),
                        "bytes": len(pdf),
                        "sha256": hashlib.sha256(pdf).hexdigest(),
                    },
                    "docx": {
                        "path": str(docx_path.relative_to(repository_root)),
                        "bytes": len(docx),
                        "sha256": hashlib.sha256(docx).hexdigest(),
                    },
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    assert pdf_path.is_file()
    assert docx_path.is_file()
    assert manifest_path.is_file()
