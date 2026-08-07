"""Query-constrained retrieval orchestration over the exact database baseline."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import UUID

from atlas.domain import CollectionSlug, Evidence, Question
from atlas.retrieval.query import RetrievalFilters, build_query_rewrite

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

    def __init__(
        self,
        repository: RetrievalRepository,
        *,
        aliases: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self._repository = repository
        self._aliases = aliases or {}
        self.last_metadata: dict[str, object] = {}

    async def retrieve(
        self,
        question: Question,
        embedding: Sequence[float],
        *,
        snapshot_id: UUID | None = None,
        top_k: int = 8,
        filters: RetrievalFilters | None = None,
    ) -> list[RetrievalRow]:
        if not 1 <= top_k <= MAX_TOP_K:
            raise ValueError(f"top_k must be between 1 and {MAX_TOP_K}")
        resolved_snapshot = snapshot_id
        if resolved_snapshot is None:
            resolved_snapshot = await self._repository.select_snapshot(question.product)
        active_filters = filters or RetrievalFilters(
            collection=question.product,
            version=question.version,
            date_from=question.date_from,
            date_to=question.date_to,
            language=question.language,
        )
        rewrite = build_query_rewrite(
            question.normalized_text,
            language=question.language,
            aliases=self._aliases,
        )
        self.last_metadata = {
            "filters": active_filters.as_metadata(),
            "original_query": rewrite.original,
            "rewritten_terms": rewrite.terms,
            "language": rewrite.language,
        }
        rows = await self._repository.search(
            collection=active_filters.collection,
            query_text=rewrite.search_text,
            embedding=list(embedding),
            top_k=top_k,
            snapshot_id=resolved_snapshot,
            version=active_filters.version,
            date_from=active_filters.date_from,
            date_to=active_filters.date_to,
        )
        return _stable_unique(_apply_available_filters(rows, active_filters), top_k)


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


def _apply_available_filters(
    rows: Sequence[RetrievalRow], filters: RetrievalFilters
) -> list[RetrievalRow]:
    """Apply metadata available on the canonical evidence without widening its schema."""

    result: list[RetrievalRow] = []
    for row in rows:
        evidence = row.evidence
        if filters.source_type is not None and evidence.source_type is not filters.source_type:
            continue
        if filters.version is not None and evidence.version_label not in {None, filters.version}:
            continue
        if filters.date_from is not None and evidence.captured_at.date() < filters.date_from:
            continue
        if filters.date_to is not None and evidence.captured_at.date() > filters.date_to:
            continue
        if (
            filters.language is not None
            and getattr(evidence, "language", filters.language) != filters.language
        ):
            continue
        haystack = f"{evidence.publisher} {evidence.source_title}".casefold()
        if filters.provider is not None and filters.provider.casefold() not in haystack:
            continue
        if filters.framework is not None and filters.framework.casefold() not in haystack:
            continue
        result.append(row)
    return result
