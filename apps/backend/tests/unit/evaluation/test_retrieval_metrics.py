from datetime import date

import pytest
from evals.evaluators.retrieval import (
    citation_precision,
    context_precision,
    context_recall,
    freshness,
    hit_at_k,
    mean_reciprocal_rank,
    result_metrics,
)


def test_retrieval_metrics_score_rank_and_coverage() -> None:
    retrieved = ["noise", "target-b", "target-a"]
    relevant = ["target-a", "target-b"]

    assert hit_at_k(retrieved, relevant, 1) == 0.0
    assert hit_at_k(retrieved, relevant, 2) == 1.0
    assert mean_reciprocal_rank(retrieved, relevant) == pytest.approx(0.5)
    assert context_precision(retrieved, relevant) == pytest.approx(2 / 3)
    assert context_recall(retrieved, relevant) == 1.0
    assert citation_precision(["target-a", "unsupported"], relevant) == 0.5


def test_freshness_is_bounded_and_deterministic() -> None:
    assert freshness(date(2026, 8, 4), date(2026, 8, 4)) == 1.0
    assert freshness("2026-08-01T00:00:00Z", "2026-08-08T00:00:00Z") == 0.0


def test_result_metrics_contains_required_plan_master_dimensions() -> None:
    metrics = result_metrics(
        ["target-a"],
        ["target-a"],
        ["target-a"],
        captured_at="2026-08-04T00:00:00Z",
        evaluated_at="2026-08-05T00:00:00Z",
    )

    assert set(metrics) == {
        "hit_at_4",
        "hit_at_8",
        "hit_at_10",
        "mrr",
        "context_precision",
        "context_recall",
        "citation_precision",
        "freshness",
    }
