# ADR-0018: Separate pricing evidence from technical documentation

## Status

Accepted — 2026-08-11

## Context

ATLAS compared a `price` criterion against a corpus whose sources were technical documentation.
That produced an honest `Sin evidencia`, but it could not answer a pricing question and did not
explain the difference between “the product has no comparable API price” and “the corpus is missing
the pricing page”.

## Decision

Pricing is a separate evidence lane. A `price` branch is routed only to sources with
`source_type=pricing`, and the source must be an official provider pricing or model-pricing page.
Technical documentation is never treated as authoritative for a price claim. The versioned
`corpus/manifests/expansion-v3-pricing.yaml` adds official OpenAI, Anthropic and Gemini pricing
pages while preserving previous corpus snapshots.

For LangGraph and LangChain as open-source frameworks, model/API token price is not a comparable
criterion. ATLAS reports `not_applicable`, not `unsupported`. A future comparison of LangSmith or a
managed deployment is a different product scope and must have its own collection/source policy.

The matrix also returns a deterministic conclusion. It does not pick a universal winner when
evidence is partial, contradictory, unavailable or not applicable. Each cited cell includes source
title, publisher, URL, bounded excerpt, capture date and version so a visitor can inspect the basis
of the result.

## Consequences

- A missing pricing page remains visible as `unsupported`; no price is invented from prose docs.
- Pricing refreshes can be audited and rolled back as immutable corpus snapshots.
- Locale changes translate explanations and conclusions without translating source excerpts, IDs,
  dates or numeric values.
- The schema and database migration add `pricing` and `not_applicable`; production application of
  the migration and ingestion of the new snapshot require the normal owner-approved Supabase run.
