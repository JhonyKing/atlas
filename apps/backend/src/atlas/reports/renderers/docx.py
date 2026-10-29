"""Branded DOCX renderer for evidence-backed comparison reports."""

from __future__ import annotations

from importlib.resources import files
from io import BytesIO
from urllib.parse import urlparse

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from atlas.reports.schemas import ReportLocale, ReportRepresentation

NAVY = "0B1B4B"
BLUE = "315FEA"
PALE = "F1F5FC"
MUTED = "61718D"
WEBSITE = "https://atlasai-lilac.vercel.app"


def _set_cell_shading(cell: object, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()  # type: ignore[attr-defined]
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def _set_cell_borders(cell: object, *, color: str = "C9D7F0", bottom_size: str = "10") -> None:
    properties = cell._tc.get_or_add_tcPr()  # type: ignore[attr-defined]
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), bottom_size if edge == "bottom" else "5")
        border.set(qn("w:color"), color if edge == "bottom" else "D9E1EF")
        borders.append(border)
    properties.append(borders)


def _add_hyperlink(paragraph: object, label: str, url: str) -> None:
    relationship_id = paragraph.part.relate_to(  # type: ignore[attr-defined]
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship_id)
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), BLUE)
    properties.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    properties.append(underline)
    run.append(properties)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)  # type: ignore[attr-defined]


def _add_page_number(paragraph: object) -> None:
    run = paragraph.add_run()  # type: ignore[attr-defined]
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run._r.addnext(field)


def _format_run(run: object, *, color: str = NAVY, size: int = 10, bold: bool = False) -> None:
    run.font.name = "Aptos"  # type: ignore[attr-defined]
    run.font.size = Pt(size)  # type: ignore[attr-defined]
    run.font.bold = bold  # type: ignore[attr-defined]
    run.font.color.rgb = RGBColor.from_string(color)  # type: ignore[attr-defined]


def _add_matrix(document: DocumentType, narrative: str) -> None:
    rows: list[tuple[str, str, str]] = []
    for line in narrative.splitlines():
        try:
            technology, rest = line.split(" / ", 1)
            criterion, value = rest.split(": ", 1)
            rows.append((technology, criterion, value))
        except ValueError:
            rows.append(("", "", line))
    table = document.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = [Inches(1.45), Inches(1.35), Inches(4.05)]
    labels = ["Tecnología", "Criterio", "Resultado y evidencia"]
    for index, cell in enumerate(table.rows[0].cells):
        cell.width = widths[index]
        _set_cell_shading(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        run = paragraph.add_run(labels[index])
        _format_run(run, color="FFFFFF", size=9, bold=True)
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cells[index].width = widths[index]
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            if row_index % 2 == 1:
                _set_cell_shading(cells[index], PALE)
            paragraph = cells[index].paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.08
            _format_run(paragraph.add_run(value), size=9)


def render_docx(report: ReportRepresentation) -> bytes:
    document = Document()
    document.core_properties.title = report.title
    document.core_properties.subject = "ATLAS technology comparison report"
    document.core_properties.author = "ATLAS"
    section_page = document.sections[0]
    section_page.top_margin = Inches(0.65)
    section_page.bottom_margin = Inches(0.7)
    section_page.left_margin = Inches(0.7)
    section_page.right_margin = Inches(0.7)
    normal = document.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor.from_string(NAVY)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.13

    is_es = report.locale is ReportLocale.ES_MX
    header_table = document.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    logo_cell, text_cell = header_table.rows[0].cells
    logo_cell.width, text_cell.width = Inches(2.0), Inches(4.85)
    for cell in (logo_cell, text_cell):
        _set_cell_shading(cell, PALE)
        _set_cell_borders(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    logo_paragraph = logo_cell.paragraphs[0]
    logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo_paragraph.add_run().add_picture(
        str(files("atlas.reports").joinpath("assets/atlas-logo-horizontal.png")),
        width=Inches(1.65),
    )
    text_paragraph = text_cell.paragraphs[0]
    text_paragraph.paragraph_format.space_after = Pt(3)
    kicker = "INFORME DE COMPARACIÓN TECNOLÓGICA" if is_es else "TECHNOLOGY COMPARISON REPORT"
    _format_run(text_paragraph.add_run(kicker + "\n"), color=BLUE, size=8, bold=True)
    _format_run(text_paragraph.add_run(report.title + "\n"), size=16, bold=True)
    run_label = "ID de comparación" if is_es else "Comparison ID"
    date_label = "Generado" if is_es else "Generated"
    _format_run(
        text_paragraph.add_run(
            f"{run_label}: {report.source_run_id}\n"
            f"{date_label}: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}"
        ),
        color=MUTED,
        size=8,
    )
    document.add_paragraph().paragraph_format.space_after = Pt(2)

    for report_section in report.sections:
        if report_section.title.lower() in {"references", "referencias"}:
            continue
        heading = document.add_heading(report_section.title, level=1)
        heading.paragraph_format.space_before = Pt(17)
        heading.paragraph_format.space_after = Pt(7)
        for run in heading.runs:
            _format_run(run, size=14, bold=True)
        if report_section.title.lower() in {"comparison matrix", "matriz de comparación"}:
            _add_matrix(document, report_section.narrative)
        else:
            paragraph = document.add_paragraph(report_section.narrative)
            paragraph.paragraph_format.space_after = Pt(10)

    references_title = "Fuentes y evidencias" if is_es else "Sources and evidence"
    heading = document.add_heading(references_title, level=1)
    heading.paragraph_format.space_before = Pt(17)
    heading.paragraph_format.space_after = Pt(7)
    for citation in report.citations:
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(2)
        run = paragraph.add_run(f"[{citation.citation_id}] ")
        _format_run(run, color=BLUE, bold=True)
        parsed = urlparse(citation.url)
        if parsed.scheme in {"https", "http"} and parsed.netloc:
            _add_hyperlink(paragraph, "Abrir fuente" if is_es else "Open source", citation.url)
        else:
            _format_run(paragraph.add_run(citation.url), color=MUTED)
        excerpt = document.add_paragraph(citation.excerpt)
        excerpt.paragraph_format.left_indent = Inches(0.2)
        excerpt.paragraph_format.space_after = Pt(9)
        for run in excerpt.runs:
            _format_run(run, color=MUTED, size=9)

    footer = section_page.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.LEFT
    footer.paragraph_format.space_before = Pt(5)
    _format_run(footer.add_run("ATLAS | "), color=MUTED, size=8)
    _add_hyperlink(footer, WEBSITE, WEBSITE)
    page_label = "Página " if is_es else "Page "
    _format_run(footer.add_run("     |     " + page_label), color=MUTED, size=8)
    _add_page_number(footer)

    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()
