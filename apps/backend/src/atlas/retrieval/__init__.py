"""Deterministic retrieval services and repository ports."""

from atlas.retrieval.context import ContextItem, EvidenceBudget, assemble_context
from atlas.retrieval.embedding_benchmark import (
    EmbeddingProfileResult,
    benchmark_embedding_profiles,
)
from atlas.retrieval.metrics import (
    RetrievalMetrics,
    calculate_metrics,
    hit_at_5,
    mean_reciprocal_rank,
)
from atlas.retrieval.query import (
    QueryRewrite,
    RetrievalFilters,
    build_query_rewrite,
    resolve_embedding_profile,
)
from atlas.retrieval.reranking import RerankerDecision, RerankMetrics, decide_reranker
from atlas.retrieval.service import RetrievalRow, RetrievalService

__all__ = [
    "ContextItem",
    "EmbeddingProfileResult",
    "EvidenceBudget",
    "QueryRewrite",
    "RerankMetrics",
    "RerankerDecision",
    "RetrievalFilters",
    "RetrievalMetrics",
    "RetrievalRow",
    "RetrievalService",
    "assemble_context",
    "benchmark_embedding_profiles",
    "build_query_rewrite",
    "calculate_metrics",
    "decide_reranker",
    "hit_at_5",
    "mean_reciprocal_rank",
    "resolve_embedding_profile",
]
