# ADR 0009: evidence-driven scale gates

## Decision

Do not claim 10k/100k MAU capacity from local tests. Record workload, commit, environment and
metrics first; introduce queue/cache/index infrastructure only when measurements justify it.
Launch gates require availability, latency, error, citation and cost evidence.
