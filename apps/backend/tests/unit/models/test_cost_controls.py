from datetime import date

import pytest

from atlas.models import (
    BenchmarkResult,
    BudgetLedger,
    CostRecord,
    PriceVersion,
    approve_promotion,
    estimate_cost,
    make_cache_key,
    select_price,
)


def test_effective_price_cost_and_budget_are_versioned() -> None:
    price = select_price(
        [PriceVersion("p1", "openai", "gpt-5.6-luna", 1, 2, date(2026, 1, 1))],
        "openai",
        "gpt-5.6-luna",
        date(2026, 8, 6),
    )
    assert estimate_cost(price, input_tokens=1_000_000, output_tokens=500_000) == 2.0
    ledger = BudgetLedger(daily_limit=2.0)
    ledger.reserve(date(2026, 8, 6), 1.5)
    assert ledger.remaining(date(2026, 8, 6)) == 0.5
    with pytest.raises(RuntimeError):
        ledger.reserve(date(2026, 8, 6), 0.6)


def test_cache_key_changes_with_versions_and_promotion_blocks_regression() -> None:
    first = make_cache_key(
        "question", tenant_scope="anonymous", corpus_version="c1", retrieval_version="r1",
        prompt_version="p1", model_version="m1", embedding_version="e1",
    )
    second = make_cache_key(
        "question", tenant_scope="anonymous", corpus_version="c2", retrieval_version="r1",
        prompt_version="p1", model_version="m1", embedding_version="e1",
    )
    assert first.as_string() != second.as_string()
    assert not approve_promotion(
        BenchmarkResult(0.8, 100, 1), BenchmarkResult(0.81, 130, 1)
    )[0]
    record = CostRecord("run-1", "openai", "gpt-5.6-luna", "price-1", 10, 5, 0.01, "daily")
    assert "prompt" not in record.as_metadata()
