"""Bounded parent-child evidence context assembly."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from atlas.retrieval.ranking import RankedEvidence


@dataclass(frozen=True, slots=True)
class EvidenceBudget:
    max_characters: int = 16000

    def __post_init__(self) -> None:
        if self.max_characters < 1:
            raise ValueError("max_characters must be positive")


@dataclass(frozen=True, slots=True)
class ContextItem:
    evidence_id: str
    text: str
    language: str | None = None


DEFAULT_BUDGET = EvidenceBudget()


def assemble_context(
    ranked: Sequence[RankedEvidence],
    *,
    budget: EvidenceBudget = DEFAULT_BUDGET,
    parent_context: dict[str, str] | None = None,
) -> list[ContextItem]:
    """Keep ranked excerpts and optional parent headings under a hard character budget."""

    parent_context = parent_context or {}
    used = 0
    result: list[ContextItem] = []
    for item in ranked:
        evidence = item.row.evidence
        prefix = parent_context.get(str(evidence.id), "")
        text = f"{prefix}\n{evidence.excerpt}" if prefix else evidence.excerpt
        remaining = budget.max_characters - used
        if remaining <= 0:
            break
        text = text[:remaining]
        if not text:
            continue
        result.append(ContextItem(str(evidence.id), text))
        used += len(text)
    return result
