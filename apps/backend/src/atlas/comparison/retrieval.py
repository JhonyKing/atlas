"""Deterministic fan-out retrieval for comparison technology branches."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import UUID

from atlas.comparison.schemas import ComparisonCriterion, ComparisonRequest
from atlas.domain import CollectionSlug, SourceType
from atlas.retrieval.service import MAX_TOP_K, RetrievalRepository, RetrievalRow


@dataclass(frozen=True, slots=True)
class ComparisonRetrievalBranch:
    technology: CollectionSlug
    criterion: ComparisonCriterion
    snapshot_id: UUID
    rows: tuple[RetrievalRow, ...]


class ComparisonBranchRetriever(Protocol):
    async def retrieve_branch(
        self,
        *,
        technology: CollectionSlug,
        criterion: ComparisonCriterion,
        snapshot_id: UUID,
        embedding: Sequence[float],
        version: str | None,
        date_from: date | None,
        date_to: date | None,
        source_type: SourceType | None,
        top_k: int,
    ) -> Sequence[RetrievalRow]: ...


class CorpusComparisonBranchRetriever:
    """Adapt the existing corpus repository to one comparison branch."""

    def __init__(self, repository: RetrievalRepository) -> None:
        self._repository = repository

    async def retrieve_branch(
        self,
        *,
        technology: CollectionSlug,
        criterion: ComparisonCriterion,
        snapshot_id: UUID,
        embedding: Sequence[float],
        version: str | None,
        date_from: date | None,
        date_to: date | None,
        source_type: SourceType | None,
        top_k: int,
    ) -> Sequence[RetrievalRow]:
        rows = await self._repository.search(
            collection=technology,
            query_text=criterion.value.replace("_", " "),
            embedding=list(embedding),
            # Pricing sources are a deliberately separate evidence lane. Ask the
            # hybrid search for a wider candidate set before applying the lane
            # filter so technical documentation cannot crowd out pricing pages.
            top_k=min(MAX_TOP_K, top_k * 4 if source_type is SourceType.PRICING else top_k),
            snapshot_id=snapshot_id,
            version=version,
            date_from=date_from,
            date_to=date_to,
        )
        if source_type is None:
            return rows
        return [row for row in rows if row.evidence.source_type is source_type]


class ComparisonRetrievalService:
    """Run one independent retrieval branch per technology and criterion."""

    def __init__(self, retriever: ComparisonBranchRetriever) -> None:
        self._retriever = retriever

    async def retrieve(
        self,
        request: ComparisonRequest,
        *,
        snapshot_id: UUID,
        embeddings: dict[ComparisonCriterion, Sequence[float]],
        top_k: int = 8,
    ) -> list[ComparisonRetrievalBranch]:
        if not 1 <= top_k <= MAX_TOP_K:
            raise ValueError(f"top_k must be between 1 and {MAX_TOP_K}")
        missing = [criterion.value for criterion in request.criteria if criterion not in embeddings]
        if missing:
            raise ValueError(f"missing embeddings for criteria: {', '.join(missing)}")

        tasks = [
            self._retrieve_one(
                request,
                technology=technology,
                criterion=criterion,
                snapshot_id=snapshot_id,
                embedding=embeddings[criterion],
                top_k=top_k,
            )
            for technology in request.technologies
            for criterion in request.criteria
        ]
        return list(await asyncio.gather(*tasks))

    async def _retrieve_one(
        self,
        request: ComparisonRequest,
        *,
        technology: CollectionSlug,
        criterion: ComparisonCriterion,
        snapshot_id: UUID,
        embedding: Sequence[float],
        top_k: int,
    ) -> ComparisonRetrievalBranch:
        rows = await self._retriever.retrieve_branch(
            technology=technology,
            criterion=criterion,
            snapshot_id=snapshot_id,
            embedding=embedding,
            version=request.version,
            date_from=request.date_from,
            date_to=request.date_to,
            source_type=request.effective_source_type(criterion),
            top_k=top_k,
        )
        return ComparisonRetrievalBranch(
            technology=technology,
            criterion=criterion,
            snapshot_id=snapshot_id,
            rows=tuple(_stable_unique(rows, top_k)),
        )


def _stable_unique(rows: Sequence[RetrievalRow], top_k: int) -> list[RetrievalRow]:
    ordered = sorted(
        rows,
        key=lambda row: (
            row.fused_rank if row.fused_rank > 0 else MAX_TOP_K + 1,
            str(row.evidence.id),
        ),
    )
    unique: list[RetrievalRow] = []
    seen: set[UUID] = set()
    for row in ordered:
        if row.evidence.id in seen:
            continue
        seen.add(row.evidence.id)
        unique.append(row)
        if len(unique) == top_k:
            break
    return unique
