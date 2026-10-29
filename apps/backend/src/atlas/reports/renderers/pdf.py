"""Branded PDF renderer for evidence-backed comparison reports."""

from __future__ import annotations

from html import escape
from importlib.resources import files
from io import BytesIO
from urllib.parse import urlparse

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.enums import TA_LEFT  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import LETTER  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.lib.units import inch  # type: ignore[import-untyped]
from reportlab.pdfgen.canvas import Canvas  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from atlas.reports.schemas import ReportLocale, ReportRepresentation

NAVY = colors.HexColor("#0B1B4B")
BLUE = colors.HexColor("#315FEA")
PALE = colors.HexColor("#F1F5FC")
MUTED = colors.HexColor("#61718D")
WEBSITE = "https://atlasai-lilac.vercel.app"


def _link(url: str) -> str | None:
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc else None


def _safe(text: str) -> str:
    return escape(text).replace("\n", "<br/>")


def _matrix_rows(narrative: str, body_style: ParagraphStyle) -> list[list[object]]:
    rows: list[list[object]] = [["Tecnología", "Criterio", "Resultado y evidencia"]]
    for line in narrative.splitlines():
        try:
            technology, rest = line.split(" / ", 1)
            criterion, value = rest.split(": ", 1)
        except ValueError:
            rows.append(["", "", Paragraph(_safe(line), body_style)])
            continue
        rows.append(
            [
                Paragraph(_safe(technology), body_style),
                Paragraph(_safe(criterion), body_style),
                Paragraph(_safe(value), body_style),
            ]
        )
    return rows


def render_pdf(report: ReportRepresentation) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.68 * inch,
        leftMargin=0.68 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.62 * inch,
        title=report.title,
        author="ATLAS",
        subject="Technology comparison report",
    )
    base = getSampleStyleSheet()
    body = ParagraphStyle(
        "AtlasBody",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=NAVY,
        spaceAfter=5,
        alignment=TA_LEFT,
    )
    heading = ParagraphStyle(
        "AtlasHeading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=NAVY,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True,
    )
    small = ParagraphStyle("AtlasSmall", parent=body, fontSize=8, leading=11, textColor=MUTED)
    title = ParagraphStyle(
        "AtlasReportTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    logo_path = files("atlas.reports").joinpath("assets/atlas-logo-horizontal.png")
    logo = Image(str(logo_path), width=1.75 * inch, height=0.52 * inch, kind="proportional")
    is_es = report.locale is ReportLocale.ES_MX
    report_label = "INFORME DE COMPARACIÓN TECNOLÓGICA" if is_es else "TECHNOLOGY COMPARISON REPORT"
    run_label = "ID de comparación" if is_es else "Comparison ID"
    date_label = "Generado" if is_es else "Generated"
    header_text = [
        Paragraph(
            report_label,
            ParagraphStyle(
                "AtlasKicker", parent=small, textColor=BLUE, fontName="Helvetica-Bold", fontSize=8.5
            ),
        ),
        Paragraph(_safe(report.title), title),
        Paragraph(
            f"{run_label}: {_safe(str(report.source_run_id))}<br/>{date_label}: "
            f"{_safe(report.generated_at.strftime('%Y-%m-%d %H:%M UTC'))}",
            small,
        ),
    ]
    header = Table([[logo, header_text]], colWidths=[2.0 * inch, 4.9 * inch])
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C9D7F0")),
                ("LINEBELOW", (0, 0), (-1, -1), 3, BLUE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 13),
            ]
        )
    )
    story: list[object] = [header, Spacer(1, 19)]
    for section in report.sections:
        if section.title.lower() in {"references", "referencias"}:
            continue
        story.append(Paragraph(_safe(section.title), heading))
        if section.title.lower() in {"comparison matrix", "matriz de comparación"}:
            matrix = Table(
                _matrix_rows(section.narrative, body),
                colWidths=[1.25 * inch, 1.2 * inch, 4.45 * inch],
                repeatRows=1,
            )
            matrix.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E1EF")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.append(matrix)
        elif section.title.lower() not in {"references", "referencias"}:
            story.append(Paragraph(_safe(section.narrative), body))
    refs_title = "Fuentes y evidencias" if is_es else "Sources and evidence"
    story.append(Paragraph(refs_title, heading))
    for index, citation in enumerate(report.citations):
        url = _link(citation.url)
        source_label = (
            f'<link href="{escape(url, quote=True)}" color="#315FEA">Abrir fuente</link>'
            if url
            else _safe(citation.url)
        )
        citation_block = [
            Paragraph(
                f'<font color="#315FEA"><b>[{_safe(citation.citation_id)}]</b></font> '
                f"{source_label}",
                body,
            ),
            Paragraph(_safe(citation.excerpt), small),
        ]
        story.append(KeepTogether(citation_block))
        if index < len(report.citations) - 1:
            story.append(Spacer(1, 6))

    def footer(page_canvas: Canvas, _doc: object) -> None:
        page_canvas.saveState()
        page_canvas.setStrokeColor(colors.HexColor("#C9D7F0"))
        page_canvas.setLineWidth(0.6)
        page_canvas.line(0.68 * inch, 0.48 * inch, 7.82 * inch, 0.48 * inch)
        page_canvas.setFont("Helvetica", 8)
        page_canvas.setFillColor(MUTED)
        page_canvas.drawString(0.68 * inch, 0.3 * inch, "ATLAS | " + WEBSITE)
        page_canvas.linkURL(
            WEBSITE,
            (0.68 * inch, 0.25 * inch, 3.3 * inch, 0.42 * inch),
            relative=0,
            thickness=0,
        )
        page_canvas.drawRightString(7.82 * inch, 0.3 * inch, str(page_canvas.getPageNumber()))
        page_canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
