"""Measured optional reranker boundary."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from atlas.retrieval.service import RetrievalRow


@dataclass(frozen=True, slots=True)
class RerankMetrics:
    quality: float
    latency_ms: float
    estimated_cost: float


@dataclass(frozen=True, slots=True)
class RerankerDecision:
    enabled: bool
    reason: str


class Reranker(Protocol):
    def rerank(self, query: str, rows: Sequence[RetrievalRow]) -> Sequence[RetrievalRow]: ...


def decide_reranker(
    baseline: RerankMetrics,
    candidate: RerankMetrics,
    *,
    min_quality_gain: float = 0.01,
    max_latency_regression: float = 0.20,
    max_cost_regression: float = 0.20,
) -> RerankerDecision:
    """Enable only after quality improves and latency/cost stay within policy."""

    if candidate.quality < baseline.quality + min_quality_gain:
        return RerankerDecision(False, "quality did not improve enough")
    if candidate.latency_ms > baseline.latency_ms * (1 + max_latency_regression):
        return RerankerDecision(False, "latency regression exceeded policy")
    if candidate.estimated_cost > baseline.estimated_cost * (1 + max_cost_regression):
        return RerankerDecision(False, "cost regression exceeded policy")
    return RerankerDecision(True, "candidate passed quality, latency and cost gates")
