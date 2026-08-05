"""Query-constrained retrieval orchestration over the exact database baseline."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import UUID

from atlas.domain import CollectionSlug, Evidence, Question

MAX_TOP_K = 50


@dataclass(frozen=True, slots=True)
class RetrievalRow:
    """One database-owned evidence record and its private ranking metadata."""

    evidence: Evidence
    keyword_rank: int | None = None
    vector_rank: int | None = None
    fused_rank: int = 0


class RetrievalRepository(Protocol):
    async def select_snapshot(self, collection: CollectionSlug | None) -> UUID: ...

    async def search(
        self,
        *,
        collection: CollectionSlug | None,
        query_text: str,
        embedding: list[float],
        top_k: int,
        snapshot_id: UUID,
        version: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> Sequence[RetrievalRow]: ...


class RetrievalService:
    """Apply bounded query policy and return unique evidence in stable order."""

    def __init__(self, repository: RetrievalRepository) -> None:
        self._repository = repository

    async def retrieve(
        self,
        question: Question,
        embedding: Sequence[float],
        *,
        snapshot_id: UUID | None = None,
        top_k: int = 8,
    ) -> list[RetrievalRow]:
        if not 1 <= top_k <= MAX_TOP_K:
            raise ValueError(f"top_k must be between 1 and {MAX_TOP_K}")
        resolved_snapshot = snapshot_id
        if resolved_snapshot is None:
            resolved_snapshot = await self._repository.select_snapshot(question.product)
        rows = await self._repository.search(
            collection=question.product,
            query_text=question.normalized_text,
            embedding=list(embedding),
            top_k=top_k,
            snapshot_id=resolved_snapshot,
            version=question.version,
            date_from=question.date_from,
            date_to=question.date_to,
        )
        return _stable_unique(rows, top_k)


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
