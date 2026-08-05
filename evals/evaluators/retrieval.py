"""Deterministic retrieval and evidence-quality metrics.

These functions intentionally accept plain identifiers and timestamps so they
can be used with fixture results, HTTP results and LangSmith evaluator runs.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date, datetime, timezone
from typing import Any


def hit_at_k(retrieved_ids: Sequence[str], relevant_ids: Iterable[str], k: int) -> float:
    """Return 1 when one relevant chunk appears in the first ``k`` results."""

    if k <= 0:
        return 0.0
    relevant = set(relevant_ids)
    return float(bool(relevant.intersection(retrieved_ids[:k])))


def mean_reciprocal_rank(retrieved_ids: Sequence[str], relevant_ids: Iterable[str]) -> float:
    """Return the reciprocal rank of the first relevant result, or zero."""

    relevant = set(relevant_ids)
    for rank, chunk_id in enumerate(retrieved_ids, 1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def context_precision(retrieved_ids: Sequence[str], relevant_ids: Iterable[str]) -> float:
    """Return the fraction of retrieved chunks that are relevant."""

    if not retrieved_ids:
        return 1.0 if not set(relevant_ids) else 0.0
    relevant = set(relevant_ids)
    return sum(chunk_id in relevant for chunk_id in retrieved_ids) / len(retrieved_ids)


def context_recall(retrieved_ids: Sequence[str], relevant_ids: Iterable[str]) -> float:
    """Return the fraction of expected chunks that were retrieved."""

    relevant = set(relevant_ids)
    if not relevant:
        return 1.0
    return len(relevant.intersection(retrieved_ids)) / len(relevant)


def citation_precision(cited_ids: Sequence[str], supported_ids: Iterable[str]) -> float:
    """Return the fraction of cited chunk IDs supported by ground truth."""

    if not cited_ids:
        return 1.0 if not set(supported_ids) else 0.0
    supported = set(supported_ids)
    return sum(citation_id in supported for citation_id in cited_ids) / len(cited_ids)


def freshness(
    captured_at: str | date | datetime,
    evaluated_at: str | date | datetime,
    max_age_days: int = 7,
) -> float:
    """Score evidence recency from 1 (new) to 0 (at or beyond max age)."""

    if max_age_days <= 0:
        raise ValueError("max_age_days must be positive")
    captured = _as_datetime(captured_at)
    evaluated = _as_datetime(evaluated_at)
    age_days = max(0.0, (evaluated - captured).total_seconds() / 86400)
    return max(0.0, 1.0 - age_days / max_age_days)


def _as_datetime(value: str | date | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    else:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def result_metrics(
    retrieved_ids: Sequence[str],
    cited_ids: Sequence[str],
    relevant_ids: Iterable[str],
    captured_at: str | date | datetime | None = None,
    evaluated_at: str | date | datetime | None = None,
) -> dict[str, float]:
    """Return all retrieval/evidence metrics for one result."""

    relevant = tuple(relevant_ids)
    metrics = {
        "hit_at_4": hit_at_k(retrieved_ids, relevant, 4),
        "hit_at_8": hit_at_k(retrieved_ids, relevant, 8),
        "hit_at_10": hit_at_k(retrieved_ids, relevant, 10),
        "mrr": mean_reciprocal_rank(retrieved_ids, relevant),
        "context_precision": context_precision(retrieved_ids, relevant),
        "context_recall": context_recall(retrieved_ids, relevant),
        "citation_precision": citation_precision(cited_ids, relevant),
    }
    if captured_at is not None and evaluated_at is not None:
        metrics["freshness"] = freshness(captured_at, evaluated_at)
    return metrics


def extract_citation_chunk_ids(result: dict[str, Any]) -> list[str]:
    """Extract chunk IDs from common citation payload shapes."""

    citation_ids: list[str] = []
    for citation in result.get("citations", []):
        if isinstance(citation, dict):
            chunk_id = citation.get("chunk_id") or citation.get("id")
            if chunk_id is not None:
                citation_ids.append(str(chunk_id))
    return citation_ids
