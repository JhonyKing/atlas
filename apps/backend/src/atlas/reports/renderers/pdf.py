"""PDF renderer for the neutral report representation."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import LETTER  # type: ignore[import-untyped]
from reportlab.lib.styles import getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.lib.units import inch  # type: ignore[import-untyped]
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer  # type: ignore[import-untyped]

from atlas.reports.schemas import ReportRepresentation


def render_pdf(report: ReportRepresentation) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(report.title, styles["Title"]),
        Paragraph(str(report.source_run_id), styles["Normal"]),
        Spacer(1, 12),
    ]
    for section in report.sections:
        story.append(Paragraph(section.title, styles["Heading2"]))
        for line in section.narrative.splitlines() or [section.narrative]:
            story.append(Paragraph(line.replace("&", "&amp;"), styles["BodyText"]))
    story.append(Paragraph("Evidence manifest", styles["Heading2"]))
    for citation in report.citations:
        text = f"[{citation.citation_id}] {citation.url} — Original evidence: {citation.excerpt}"
        story.append(Paragraph(text.replace("&", "&amp;"), styles["BodyText"]))
    document.build(story)
    return buffer.getvalue()
