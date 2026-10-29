"""Build a neutral, citation-first report representation from a completed comparison run."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from atlas.api.routes.comparisons import ComparisonRunResponse
from atlas.reports.schemas import (
    ReportCitation,
    ReportLocale,
    ReportRepresentation,
    ReportSection,
    ReportSpec,
)


class ComparisonSource(Protocol):
    async def get_status(
        self, run_id: UUID, *, visitor_key_hash: str
    ) -> ComparisonRunResponse | None: ...


class ReportPlanningError(ValueError):
    """The source run cannot support a cited report."""


def _label(value: str, locale: ReportLocale) -> str:
    if locale is ReportLocale.ES_MX:
        return {
            "Executive summary": "Resumen ejecutivo",
            "Comparison matrix": "Matriz de comparación",
            "Limitations": "Limitaciones",
            "References": "Referencias",
        }.get(value, value)
    return value


def _technology_label(value: str) -> str:
    known = {"openai": "OpenAI", "anthropic": "Anthropic", "google": "Google"}
    return known.get(value.lower(), value.replace("-", " ").replace("_", " ").title())


def _criterion_label(value: str, locale: ReportLocale) -> str:
    labels = {
        "capability": ("Capacidad", "Capability"),
        "tool_calling": ("Llamada a herramientas", "Tool calling"),
        "context": ("Ventana de contexto", "Context window"),
        "latency": ("Latencia", "Latency"),
        "price": ("Precio", "Price"),
        "license": ("Licencia", "License"),
        "freshness": ("Vigencia", "Freshness"),
        "operational_risk": ("Riesgo operativo", "Operational risk"),
    }
    fallback = value.replace("_", " ").title()
    return labels.get(value, (fallback, fallback))[0 if locale is ReportLocale.ES_MX else 1]


async def plan_report(
    spec: ReportSpec,
    *,
    owner_key_hash: str,
    source: ComparisonSource,
    clock: Callable[[], datetime] | None = None,
) -> ReportRepresentation:
    """Plan a report without allowing the planner to invent evidence."""

    if spec.report_type.value != "comparison":
        raise ReportPlanningError("report_type_not_implemented")
    run = await source.get_status(spec.source_run_id, visitor_key_hash=owner_key_hash)
    if run is None:
        raise ReportPlanningError("source_run_not_found")
    if run.status != "completed" or run.matrix is None:
        raise ReportPlanningError("source_run_not_completed")

    citations: list[ReportCitation] = []
    evidence_by_id = {
        evidence.id: evidence for cell in run.matrix.cells for evidence in cell.evidence
    }
    seen: set[UUID] = set()
    for cell in run.matrix.cells:
        for evidence_id in cell.evidence_ids:
            if evidence_id in seen:
                continue
            seen.add(evidence_id)
            citations.append(
                ReportCitation(
                    citation_id=f"E{len(citations) + 1}",
                    source_run_id=spec.source_run_id,
                    evidence_id=evidence_id,
                    url=(
                        evidence_by_id[evidence_id].canonical_url
                        if evidence_id in evidence_by_id
                        else f"atlas://comparison/{spec.source_run_id}/evidence/{evidence_id}"
                    ),
                    excerpt=(
                        evidence_by_id[evidence_id].excerpt[:2000]
                        if evidence_id in evidence_by_id
                        else (
                            "Original evidence is available in the source run evidence panel; "
                            f"citation identity {evidence_id} is preserved."
                        )
                    ),
                )
            )
    if not citations:
        raise ReportPlanningError("source_run_has_no_evidence")

    citation_ids = [citation.citation_id for citation in citations]
    citation_by_evidence = {citation.evidence_id: citation.citation_id for citation in citations}
    matrix_lines = []
    for cell in run.matrix.cells:
        value = cell.value or cell.explanation or "No supported evidence"
        refs = ", ".join(citation_by_evidence[evidence_id] for evidence_id in cell.evidence_ids)
        matrix_lines.append(
            f"{_technology_label(cell.technology_id.value)} / "
            f"{_criterion_label(cell.criterion_id.value, spec.locale)}: {value} "
            f"[{refs or 'abstained'}]"
        )
    summary = run.matrix.summary or "Comparison completed with evidence-linked cells."
    if spec.locale is ReportLocale.ES_MX:
        summary = f"{summary} Este informe conserva las referencias de evidencia originales."

    sections = [
        ReportSection(
            title=_label("Executive summary", spec.locale),
            narrative=summary,
            citation_ids=citation_ids,
        ),
        ReportSection(
            title=_label("Comparison matrix", spec.locale),
            narrative="\n".join(matrix_lines),
            citation_ids=citation_ids,
        ),
        ReportSection(
            title=_label("Limitations", spec.locale),
            narrative=(
                "Unsupported or contradictory cells remain explicitly marked; this report "
                "does not infer missing evidence."
                if spec.locale is ReportLocale.EN_US
                else "Las celdas no compatibles o contradictorias permanecen marcadas; "
                "el informe no infiere evidencia faltante."
            ),
            citation_ids=citation_ids,
        ),
        ReportSection(
            title=_label("References", spec.locale),
            narrative="\n".join(f"[{c.citation_id}] {c.url}" for c in citations),
            citation_ids=citation_ids,
            is_factual=False,
        ),
    ]
    return ReportRepresentation(
        title=(
            "Technology comparison report"
            if spec.locale is ReportLocale.EN_US
            else "Informe de comparación tecnológica"
        ),
        locale=spec.locale,
        source_run_id=spec.source_run_id,
        sections=sections,
        citations=citations,
        generated_at=(clock or (lambda: datetime.now(UTC)))(),
    )
