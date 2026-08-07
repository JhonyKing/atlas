"""Deterministic evidence ranking policies."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from atlas.retrieval.service import RetrievalRow


@dataclass(frozen=True, slots=True)
class RankedEvidence:
    row: RetrievalRow
    score: float
    diversity_key: str


def rank_evidence(
    rows: Sequence[RetrievalRow],
    *,
    limit: int,
    now: datetime | None = None,
    authority: dict[str, float] | None = None,
) -> list[RankedEvidence]:
    """Deduplicate by evidence and prefer authority, freshness and source diversity."""

    if limit < 1:
        raise ValueError("limit must be positive")
    reference = now or datetime.now(UTC)
    authority = authority or {}
    candidates: list[RankedEvidence] = []
    seen: set[UUID] = set()
    for row in rows:
        evidence = row.evidence
        if evidence.id in seen:
            continue
        seen.add(evidence.id)
        age_days = max(0.0, (reference - evidence.captured_at).total_seconds() / 86400)
        freshness = 1.0 / (1.0 + age_days / 30.0)
        score = authority.get(evidence.publisher.casefold(), 0.5) * 0.6 + freshness * 0.3
        if row.fused_rank > 0:
            score += 0.1 / row.fused_rank
        candidates.append(
            RankedEvidence(row=row, score=score, diversity_key=evidence.publisher.casefold())
        )
    selected: list[RankedEvidence] = []
    used_publishers: set[str] = set()
    remaining = sorted(candidates, key=lambda item: (-item.score, str(item.row.evidence.id)))
    while remaining and len(selected) < limit:
        diverse = next(
            (item for item in remaining if item.diversity_key not in used_publishers), remaining[0]
        )
        remaining.remove(diverse)
        selected.append(diverse)
        used_publishers.add(diverse.diversity_key)
    return selected
