# Architecture — scale, reliability, and SLOs

Feature 010 separates workload definition from measurement and gate evaluation. `atlas.slo` is a
pure policy layer: it consumes a complete measurement record and returns pass/fail reasons without
assuming a queue, Redis, HNSW index or production capacity. This keeps infrastructure decisions
evidence-driven and makes missing measurements fail closed.
