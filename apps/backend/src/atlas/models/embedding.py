"""Locale-aware embedding profile selection without changing Evidence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmbeddingSelection:
    provider: str
    profile: str
    fallback: bool
    reason: str


def select_embedding_profile(
    language: str,
    profiles: dict[str, str],
    *,
    baseline_provider: str = "baseline",
) -> EmbeddingSelection:
    provider = profiles.get(language)
    if provider is not None:
        return EmbeddingSelection(
            provider, f"{provider}:{language}", False, "language profile available"
        )
    return EmbeddingSelection(
        baseline_provider,
        f"{baseline_provider}:multilingual",
        True,
        "language profile unavailable; baseline fallback",
    )
