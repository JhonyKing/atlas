from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import HttpUrl

from atlas.domain import Evidence, SourceType
from atlas.retrieval.context import EvidenceBudget, assemble_context
from atlas.retrieval.metrics import calculate_metrics, hit_at_5, mean_reciprocal_rank
from atlas.retrieval.query import build_query_rewrite, resolve_embedding_profile
from atlas.retrieval.ranking import rank_evidence
from atlas.retrieval.reranking import RerankMetrics, decide_reranker
from atlas.retrieval.service import RetrievalRow


def _row(number: int, publisher: str, *, age_days: int = 1) -> RetrievalRow:
    return RetrievalRow(
        evidence=Evidence(
            id=UUID(f"00000000-0000-0000-0000-{number:012d}"),
            source_title=f"Source {number}",
            publisher=publisher,
            canonical_url=HttpUrl("https://docs.example.test/reference"),
            excerpt=f"Evidence excerpt {number}",
            captured_at=datetime.now(UTC) - timedelta(days=age_days),
            source_type=SourceType.DOCUMENTATION,
        ),
        fused_rank=number,
    )


def test_rewrite_is_bounded_and_preserves_original() -> None:
    rewrite = build_query_rewrite(
        "¿Cómo funciona LangGraph?",
        language="es-MX",
        aliases={"langgraph": ("LangGraph StateGraph", "https://unsafe.example.test")},
    )
    assert rewrite.original == "¿Cómo funciona LangGraph?"
    assert rewrite.language == "es-MX"
    assert rewrite.terms == ("LangGraph StateGraph",)


def test_ranking_deduplicates_and_diversifies_publishers() -> None:
    rows = [_row(1, "Official", age_days=1), _row(2, "Official", age_days=2), _row(3, "Community")]
    ranked = rank_evidence(rows, limit=2, now=datetime.now(UTC), authority={"official": 1.0})
    assert [item.row.evidence.id for item in ranked] == [rows[0].evidence.id, rows[2].evidence.id]


def test_context_budget_is_hard_and_parent_context_is_kept() -> None:
    ranked = rank_evidence([_row(1, "Official"), _row(2, "Other")], limit=2)
    context = assemble_context(
        ranked,
        budget=EvidenceBudget(max_characters=28),
        parent_context={str(ranked[0].row.evidence.id): "Parent heading"},
    )
    assert sum(len(item.text) for item in context) <= 28
    assert context[0].text.startswith("Parent heading")


def test_reranker_requires_quality_gain_without_regression() -> None:
    baseline = RerankMetrics(quality=0.70, latency_ms=100, estimated_cost=1)
    assert not decide_reranker(baseline, RerankMetrics(0.70, 90, 1)).enabled
    assert not decide_reranker(baseline, RerankMetrics(0.75, 130, 1)).enabled
    assert decide_reranker(baseline, RerankMetrics(0.75, 110, 1.1)).enabled


def test_reranker_rejects_cost_regression_and_embedding_has_safe_fallback() -> None:
    baseline = RerankMetrics(quality=0.70, latency_ms=100, estimated_cost=1)
    assert not decide_reranker(baseline, RerankMetrics(0.75, 110, 1.3)).enabled
    assert resolve_embedding_profile("es-MX", {"baseline-multilingual:en-US"}) == (
        "baseline-multilingual",
        True,
    )


def test_retrieval_metrics_are_deterministic() -> None:
    results = [["a", "b", "c"], ["target", "z"]]
    relevant = [{"b"}, {"target"}]
    assert hit_at_5(results, relevant) == 1.0
    assert mean_reciprocal_rank(results, relevant) == 0.75
    metrics = calculate_metrics(
        results,
        relevant,
        predicted_context=["b"],
        relevant_context={"b", "c"},
        cited=["b"],
        supported_citations={"b"},
        fresh_flags=[True, False],
        latency_ms=12,
        estimated_cost=0.01,
    )
    assert metrics.context_recall == 0.5
    assert metrics.citation_precision == 1.0
    assert metrics.latency_ms == 12
