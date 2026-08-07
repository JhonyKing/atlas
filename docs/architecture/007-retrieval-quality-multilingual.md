# Architecture — retrieval quality and multilingual evidence

Feature 007 keeps retrieval provider-independent and composes five narrow policies:

1. `query.py` preserves the original question and creates bounded aliases/synonyms plus filter
   metadata. URL-like expansions are rejected, so rewriting cannot create a new destination.
2. `ranking.py` removes duplicate evidence IDs, scores authority/freshness deterministically, and
   prefers different publishers when filling the result window.
3. `context.py` adds optional parent headings while enforcing a hard character budget.
4. `reranking.py` exposes a protocol but enables a candidate only after quality improves and
   latency/cost regressions stay within policy.
5. `metrics.py` provides reproducible Hit@5, MRR, precision/recall, citation precision and
   freshness helpers.

`RetrievalService` records the active filters and rewrite metadata while preserving existing
`Question`, `Evidence`, and repository contracts. A missing language-specific embedding profile
therefore falls back to the existing baseline instead of changing the public evidence schema.
