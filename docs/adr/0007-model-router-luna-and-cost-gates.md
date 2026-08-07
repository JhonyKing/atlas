# ADR 0007: Luna default with measured provider and cost gates

## Decision

Use `gpt-5.6-luna` as the configured primary answer model, but keep graph nodes dependent on a
provider-independent adapter. Routing, retries, pricing, budgets, cache invalidation and promotion
are explicit typed policies. No model change is promoted without paired quality, latency and cost
evidence.

## Consequence

The portfolio can demonstrate a cheap default and a reversible fallback path, while production
credentials and live provider benchmarks remain deployment evidence rather than local assumptions.
