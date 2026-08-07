"""Explicit comparison workflow: retrieve, extract, normalize, and gate evidence."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Protocol
from uuid import UUID

from atlas.comparison.normalization import ComparisonObservation, normalize_observations
from atlas.comparison.retrieval import ComparisonRetrievalBranch
from atlas.comparison.schemas import (
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
    ComparisonRequest,
)


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
        self, branch: ComparisonRetrievalBranch
    ) -> Sequence[ComparisonObservation]: ...


class ComparisonWorkflow:
    """Keep matrix construction explicit and prevent unverified output."""

    def __init__(
        self,
        retrieval: ComparisonRetrieval,
        extractor: ComparisonObservationExtractor,
    ) -> None:
        self._retrieval = retrieval
        self._extractor = extractor

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
        cells = []
        for branch in branches:
            _check_cancelled(is_cancelled)
            observations = list(await self._extractor.extract(branch))
            cells.append(
                normalize_observations(
                    technology_id=branch.technology,
                    criterion_id=branch.criterion,
                    observations=observations,
                )
            )
        matrix = ComparisonMatrix(
            technology_ids=request.technologies,
            criterion_ids=request.criteria,
            cells=cells,
        )
        _check_evidence_gate(matrix)
        _check_cancelled(is_cancelled)
        return matrix


def _check_cancelled(is_cancelled: Callable[[], bool] | None) -> None:
    if is_cancelled is not None and is_cancelled():
        raise ComparisonWorkflowCancelled("comparison was cancelled")


def _check_evidence_gate(matrix: ComparisonMatrix) -> None:
    for cell in matrix.cells:
        if cell.state is ComparisonCellState.UNSUPPORTED:
            if cell.evidence_ids:
                raise ValueError("unsupported comparison cells cannot cite evidence")
            if not cell.explanation:
                raise ValueError("unsupported comparison cells require an explanation")
            continue
        if not cell.evidence_ids:
            raise ValueError("populated comparison cells require evidence")
