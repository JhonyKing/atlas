"""Deterministic profile comparison without importing an embedding provider SDK."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from atlas.retrieval.metrics import hit_at_5, mean_reciprocal_rank


@dataclass(frozen=True, slots=True)
class EmbeddingProfileResult:
    profile: str
    hit_at_5: float
    mrr: float
    fallback_cases: int = 0


def benchmark_embedding_profiles(
    profiles: dict[str, Sequence[Sequence[str]]],
    relevant: Sequence[set[str]],
    *,
    fallback_profile: str,
) -> list[EmbeddingProfileResult]:
    """Compare versioned fixture outputs and expose which profile is the fallback."""

    results: list[EmbeddingProfileResult] = []
    for name, rows in sorted(profiles.items()):
        results.append(
            EmbeddingProfileResult(
                profile=name,
                hit_at_5=hit_at_5(rows, relevant),
                mrr=mean_reciprocal_rank(rows, relevant),
                fallback_cases=len(rows) if name == fallback_profile else 0,
            )
        )
    return results
