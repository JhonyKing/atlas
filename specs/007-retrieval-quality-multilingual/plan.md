# Implementation Plan: Retrieval Quality and Multilingual Evidence

**Branch**: `codex/007-retrieval-quality-multilingual` | **Date**: 2026-08-06 | **Spec**:
`specs/007-retrieval-quality-multilingual/spec.md`

## Summary

Extend the current exact hybrid retrieval baseline with typed query rewriting, filters, diversity,
bounded context assembly, optional measured reranking, multilingual metadata and a reproducible
evaluation harness. The baseline remains the safe default until metrics approve an alternative.

## Technical Context

- Python 3.13, Pydantic v2, existing `RetrievalService`/`RetrievalRepository`, PostgreSQL snapshot
  boundary, pytest, Ruff, mypy and deterministic JSONL evals.
- New ranking and rewrite behavior lives behind narrow protocols; providers and embedding profiles
  never leak into `Evidence` or answer contracts.
- Scores and metrics are content-light: IDs, ranks, language, version, latency and cost classes only.

## Constitution Check

- Evidence over fluency: rankings retain source IDs, capture/version metadata and contradiction state.
- Test/evaluate first: baseline and candidate metrics are paired before any enablement.
- Provider independence: rewrite, embedding and reranker protocols hide provider SDKs.
- Security/privacy: rewrites cannot create destinations; evaluation fixtures contain no private data.
- Observable/cost-aware: retrieval records filter, version, latency and estimated cost metadata.
- Small vertical slice: deterministic quality harness precedes production-scale reranking.

## Architecture

1. `query.py` builds bounded original/rewritten terms and filter metadata.
2. `ranking.py` applies stable deduplication, diversity and authority/freshness scoring.
3. `context.py` assembles parent/child windows under a hard evidence budget.
4. `reranking.py` defines baseline/candidate adapter and measured enablement decision.
5. `metrics.py` computes Hit@5, MRR, context precision/recall, citation precision, freshness,
   latency and cost for versioned cases.
6. `RetrievalService` composes these policies while preserving existing repository calls.

## Project Structure

```text
apps/backend/src/atlas/retrieval/
├── query.py       # rewrites and typed filters
├── ranking.py     # diversity, deduplication, authority/freshness
├── context.py     # parent-child windows and evidence budget
├── reranking.py   # measured optional adapter
└── metrics.py     # deterministic quality metrics
apps/backend/tests/unit/retrieval/
apps/backend/tests/integration/retrieval/
apps/backend/tests/security/test_retrieval_quality.py
evals/cases/007-retrieval-quality-multilingual.jsonl
docs/verification/007-retrieval-quality-multilingual.md
```

## Implementation Sequence

1. Add failing rewrite/filter/ranking/context/metrics/security tests.
2. Implement query preparation, filters and deterministic ranking/context policies.
3. Add reranker adapter and baseline comparison decision; keep baseline default.
4. Extend retrieval service and multilingual metadata without changing evidence schemas.
5. Add regression evals, run full tests/lint/mypy, update documentation and converge.
