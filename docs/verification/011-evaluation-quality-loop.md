# Feature 011 — evaluation, observability, and quality loop

## Evidence

| Check | Result |
|---|---:|
| Evaluation suite | 17 passed |
| Regression command | 17 passed |
| Full backend regression | 298 passed, 4 skipped |
| Frontend lint/typecheck | passed |
| Ruff/mypy quality evaluators | passed |
| Dataset manifest | `evals/manifests/011-quality-loop.json` |
| Private/public boundary | aggregate methodology only; content excluded |

The local deterministic loop covers schema and citation-link checks, duplicate detection, retrieval
metrics already present in the repository, versioned judge metadata, online security/anomaly signals,
safe trace tags and a fail-closed promotion gate. External judge runs and human annotation remain
opt-in evidence.
