# ADR 0010: deterministic quality before model judges

## Decision

Deterministic schema, citation, retrieval, freshness and report evaluators are release gates. Model
judges may add advisory quality signals only through a versioned rubric with bias controls. Private
feedback and difficult cases stay in a minimized queue; public output contains aggregates and
methodology.
