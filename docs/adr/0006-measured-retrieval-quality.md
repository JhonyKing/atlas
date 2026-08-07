# ADR 0006: measured retrieval quality before reranking

## Status

Accepted for Feature 007.

## Decision

The exact hybrid baseline remains the default. Query rewriting, diversity, evidence budgets and
reranking are provider-independent policies. A reranker can be enabled only when a paired,
versioned evaluation shows a minimum quality gain and no more than 20% latency or estimated-cost
regression. If it times out, returns malformed scores, or fails the gate, ATLAS records the reason
and keeps the baseline.

## Consequences

This makes retrieval changes reproducible and reversible, but requires maintaining JSONL cases and
recording benchmark evidence before changing the production default.
