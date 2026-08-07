"""Generate inspected Feature 003 DOCX/PDF evidence from the deterministic report fixture."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "backend"))

from tests.unit.reports.test_planner import Source, _completed  # noqa: E402
from atlas.reports.planner import plan_report  # noqa: E402
from atlas.reports.renderers.docx import render_docx  # noqa: E402
from atlas.reports.renderers.pdf import render_pdf  # noqa: E402
from atlas.reports.schemas import ReportSpec  # noqa: E402
from atlas.reports.validation import validate_docx, validate_pdf  # noqa: E402


async def main() -> None:
    source = _completed()
    report = await plan_report(
        ReportSpec(source_run_id=source.run_id, audience="engineer", scope="comparison"),
        owner_key_hash="fixture-owner",
        source=Source(source),
    )
    output = Path("docs/verification/artifacts/003")
    output.mkdir(parents=True, exist_ok=True)
    docx = render_docx(report)
    pdf = render_pdf(report)
    validate_docx(docx, report)
    validate_pdf(pdf, report)
    (output / "atlas-report-fixture.docx").write_bytes(docx)
    (output / "atlas-report-fixture.pdf").write_bytes(pdf)
    print(f"docx_bytes={len(docx)} pdf_bytes={len(pdf)} citations={len(report.citations)}")


if __name__ == "__main__":
    asyncio.run(main())
