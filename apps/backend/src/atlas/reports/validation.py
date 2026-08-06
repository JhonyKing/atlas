"""Fail-closed report and artifact validation."""

from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

from pypdf import PdfReader

from atlas.reports.schemas import ReportRepresentation


class ReportValidationError(ValueError):
    """A report or artifact is not safe to publish."""


def validate_representation(report: ReportRepresentation) -> None:
    citation_ids = {citation.citation_id for citation in report.citations}
    if not citation_ids:
        raise ReportValidationError("report_has_no_citations")
    for section in report.sections:
        if section.is_factual and not section.citation_ids:
            raise ReportValidationError("factual_section_has_no_citation")
        if not set(section.citation_ids).issubset(citation_ids):
            raise ReportValidationError("unknown_citation")


def validate_docx(content: bytes, report: ReportRepresentation) -> None:
    if not content:
        raise ReportValidationError("empty_docx")
    try:
        with ZipFile(BytesIO(content)) as archive:
            xml = archive.read("word/document.xml").decode("utf-8")
    except Exception as exc:
        raise ReportValidationError("malformed_docx") from exc
    for citation in report.citations:
        if citation.citation_id not in xml or citation.url not in xml:
            raise ReportValidationError("docx_missing_citation")


def validate_pdf(content: bytes, report: ReportRepresentation) -> None:
    if not content:
        raise ReportValidationError("empty_pdf")
    try:
        text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
    except Exception as exc:
        raise ReportValidationError("malformed_pdf") from exc
    compact_text = "".join(text.split())
    for citation in report.citations:
        if citation.citation_id not in text or "".join(citation.url.split()) not in compact_text:
            raise ReportValidationError("pdf_missing_citation")
