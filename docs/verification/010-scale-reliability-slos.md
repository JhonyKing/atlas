# Feature 010 — scale, reliability, and SLOs

## Current evidence

| Check | Result |
|---|---:|
| SLO gate tests | 4 passed |
| Full backend regression | 294 passed, 4 skipped |
| Frontend lint/typecheck | passed |
| `pnpm test:slo` | passed |
| Ruff/mypy for SLO package | passed |
| Workload fixture | `evals/load/010-slo-smoke.json` |
| Deterministic gate artifact | `docs/verification/010-slo-smoke-metrics.json` |

The gate fails closed for missing metrics and checks availability, uncontrolled errors, p95,
TTFT, report duration, citation precision and cost budget. No live load or production capacity
claim is made by this local deterministic slice.
The artifact is explicitly marked `measured: false`; it demonstrates gate behavior, not live capacity.
