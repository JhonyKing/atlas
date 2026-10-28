"""Explicit comparison workflow: retrieve, extract, normalize, and gate evidence."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping, Sequence
from typing import Literal, Protocol
from uuid import UUID

from atlas.comparison.normalization import ComparisonObservation, normalize_observations
from atlas.comparison.retrieval import ComparisonRetrievalBranch
from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonEvidence,
    ComparisonMatrix,
    ComparisonRequest,
)
from atlas.domain import Evidence


class ComparisonWorkflowCancelled(RuntimeError):
    """The visitor cancelled before a verified matrix could be published."""


class ComparisonRetrieval(Protocol):
    async def retrieve(
        self,
        request: ComparisonRequest,
        *,
        snapshot_id: UUID,
        embeddings: dict[ComparisonCriterion, Sequence[float]],
        top_k: int = 8,
    ) -> list[ComparisonRetrievalBranch]: ...


class ComparisonObservationExtractor(Protocol):
    async def extract(
        self,
        branch: ComparisonRetrievalBranch,
        *,
        language: Literal["en-US", "es-MX"],
    ) -> Sequence[ComparisonObservation]: ...


class ComparisonWorkflow:
    """Keep matrix construction explicit and prevent unverified output."""

    def __init__(
        self,
        retrieval: ComparisonRetrieval,
        extractor: ComparisonObservationExtractor,
        *,
        max_extraction_concurrency: int = 4,
    ) -> None:
        if max_extraction_concurrency < 1:
            raise ValueError("max_extraction_concurrency must be positive")
        self._retrieval = retrieval
        self._extractor = extractor
        self._max_extraction_concurrency = max_extraction_concurrency

    async def run(
        self,
        request: ComparisonRequest,
        *,
        snapshot_id: UUID,
        embeddings: Mapping[ComparisonCriterion, Sequence[float]],
        top_k: int = 8,
        is_cancelled: Callable[[], bool] | None = None,
    ) -> ComparisonMatrix:
        _check_cancelled(is_cancelled)
        branches = await self._retrieval.retrieve(
            request,
            snapshot_id=snapshot_id,
            embeddings=dict(embeddings),
            top_k=top_k,
        )
        semaphore = asyncio.Semaphore(self._max_extraction_concurrency)

        async def extract_branch(branch: ComparisonRetrievalBranch) -> ComparisonCell:
            async with semaphore:
                _check_cancelled(is_cancelled)
                if _is_not_applicable(branch):
                    return normalize_observations(
                        technology_id=branch.technology,
                        criterion_id=branch.criterion,
                        observations=[],
                        language=request.language,
                        not_applicable=True,
                    )
                observations = list(
                    await self._extractor.extract(branch, language=request.language)
                )
                _check_cancelled(is_cancelled)
                cell = normalize_observations(
                    technology_id=branch.technology,
                    criterion_id=branch.criterion,
                    observations=observations,
                    language=request.language,
                )
                if cell.evidence_ids:
                    cell = cell.model_copy(
                        update={
                            "evidence": [
                                _comparison_evidence(row.evidence)
                                for row in branch.rows
                                if row.evidence.id in set(cell.evidence_ids)
                            ]
                        }
                    )
                return cell

        tasks = [asyncio.create_task(extract_branch(branch)) for branch in branches]
        try:
            cells = list(await asyncio.gather(*tasks))
        except BaseException:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        matrix = ComparisonMatrix(
            technology_ids=request.technologies,
            criterion_ids=request.criteria,
            cells=cells,
            summary=_build_summary(cells, language=request.language),
        )
        _check_evidence_links(matrix, branches)
        _check_evidence_gate(matrix)
        _check_cancelled(is_cancelled)
        return matrix


def _check_cancelled(is_cancelled: Callable[[], bool] | None) -> None:
    if is_cancelled is not None and is_cancelled():
        raise ComparisonWorkflowCancelled("comparison was cancelled")


def _check_evidence_gate(matrix: ComparisonMatrix) -> None:
    for cell in matrix.cells:
        if cell.state in {
            ComparisonCellState.UNSUPPORTED,
            ComparisonCellState.NOT_APPLICABLE,
        }:
            if cell.evidence_ids:
                raise ValueError("unsupported comparison cells cannot cite evidence")
            if not cell.explanation:
                raise ValueError("unsupported comparison cells require an explanation")
            continue
        if not cell.evidence_ids:
            raise ValueError("populated comparison cells require evidence")


def _check_evidence_links(
    matrix: ComparisonMatrix, branches: Sequence[ComparisonRetrievalBranch]
) -> None:
    """Ensure each published citation came from the exact branch that built the cell."""

    allowed_by_coordinate = {
        (branch.technology, branch.criterion): {row.evidence.id for row in branch.rows}
        for branch in branches
    }
    for cell in matrix.cells:
        allowed = allowed_by_coordinate.get((cell.technology_id, cell.criterion_id), set())
        unexpected = set(cell.evidence_ids).difference(allowed)
        if unexpected:
            raise ValueError(
                "comparison cell cited evidence outside its retrieval branch: "
                + ", ".join(sorted(str(evidence_id) for evidence_id in unexpected))
            )


def _is_not_applicable(branch: ComparisonRetrievalBranch) -> bool:
    """Open-source frameworks do not have a comparable model/API token price."""

    return branch.criterion is ComparisonCriterion.PRICE and branch.technology.value in {
        "langgraph",
        "langchain",
    }


def _comparison_evidence(evidence: Evidence) -> ComparisonEvidence:
    return ComparisonEvidence(
        id=evidence.id,
        source_title=evidence.source_title,
        publisher=evidence.publisher,
        canonical_url=str(evidence.canonical_url),
        source_type=evidence.source_type,
        excerpt=evidence.excerpt,
        captured_at=evidence.captured_at,
        version_label=evidence.version_label,
    )


def _build_summary(
    cells: Sequence[ComparisonCell], *, language: Literal["en-US", "es-MX"]
) -> str:
    unsupported = sum(cell.state is ComparisonCellState.UNSUPPORTED for cell in cells)
    not_applicable = sum(cell.state is ComparisonCellState.NOT_APPLICABLE for cell in cells)
    partial = sum(cell.state is ComparisonCellState.PARTIAL for cell in cells)
    contradictory = sum(cell.state is ComparisonCellState.CONTRADICTORY for cell in cells)
    if language == "es-MX":
        if not unsupported and not not_applicable and not partial and not contradictory:
            return (
                "Conclusión: hay valores comparables respaldados; revisa las fuentes antes de "
                "decidir."
            )
        reasons: list[str] = []
        if partial:
            reasons.append("evidencia parcial")
        if contradictory:
            reasons.append("evidencia contradictoria")
        if unsupported:
            reasons.append("datos comparables no encontrados")
        if not_applicable:
            reasons.append("criterios que no aplican al producto")
        return "Conclusión: no se puede declarar un ganador todavía; " + ", ".join(reasons) + "."
    if not unsupported and not not_applicable and not partial and not contradictory:
        return "Conclusion: comparable values are supported; inspect the sources before deciding."
    reasons_en: list[str] = []
    if partial:
        reasons_en.append("partial evidence")
    if contradictory:
        reasons_en.append("contradictory evidence")
    if unsupported:
        reasons_en.append("no comparable data found")
    if not_applicable:
        reasons_en.append("criteria that do not apply to the product")
    return "Conclusion: no winner can be declared yet; " + ", ".join(reasons_en) + "."
