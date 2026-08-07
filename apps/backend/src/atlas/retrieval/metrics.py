"""Small deterministic metrics for retrieval evaluation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalMetrics:
    hit_at_5: float
    mrr: float
    context_precision: float
    context_recall: float
    citation_precision: float
    freshness: float
    latency_ms: float = 0.0
    estimated_cost: float = 0.0


def hit_at_5(results: Sequence[Sequence[str]], relevant: Sequence[set[str]]) -> float:
    if not results:
        return 0.0
    return sum(
        bool(set(row[:5]) & truth) for row, truth in zip(results, relevant, strict=True)
    ) / len(results)


def mean_reciprocal_rank(results: Sequence[Sequence[str]], relevant: Sequence[set[str]]) -> float:
    if not results:
        return 0.0
    values = []
    for row, truth in zip(results, relevant, strict=True):
        rank = next((index for index, item in enumerate(row, 1) if item in truth), 0)
        values.append(1 / rank if rank else 0.0)
    return sum(values) / len(values)


def set_precision(predicted: Sequence[str], relevant: set[str]) -> float:
    return len(set(predicted) & relevant) / len(set(predicted)) if predicted else 0.0


def set_recall(predicted: Sequence[str], relevant: set[str]) -> float:
    return len(set(predicted) & relevant) / len(relevant) if relevant else 0.0


def citation_precision(cited: Sequence[str], supported: set[str]) -> float:
    return set_precision(cited, supported)


def freshness_accuracy(fresh_flags: Sequence[bool]) -> float:
    return sum(fresh_flags) / len(fresh_flags) if fresh_flags else 0.0


def calculate_metrics(
    results: Sequence[Sequence[str]],
    relevant: Sequence[set[str]],
    *,
    predicted_context: Sequence[str] = (),
    relevant_context: set[str] | None = None,
    cited: Sequence[str] = (),
    supported_citations: set[str] | None = None,
    fresh_flags: Sequence[bool] = (),
    latency_ms: float = 0.0,
    estimated_cost: float = 0.0,
) -> RetrievalMetrics:
    """Compute the complete metric record used by the offline harness."""

    context_truth = relevant_context or set()
    citation_truth = supported_citations or set()
    return RetrievalMetrics(
        hit_at_5=hit_at_5(results, relevant),
        mrr=mean_reciprocal_rank(results, relevant),
        context_precision=set_precision(predicted_context, context_truth),
        context_recall=set_recall(predicted_context, context_truth),
        citation_precision=citation_precision(cited, citation_truth),
        freshness=freshness_accuracy(fresh_flags),
        latency_ms=latency_ms,
        estimated_cost=estimated_cost,
    )
