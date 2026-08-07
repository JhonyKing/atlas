# Feature 014 — real multi-document corpus and evaluation harness

| Check | Result |
|---|---:|
| Ingestion unit/contract/integration tests | **43 passed, 3 skipped** |
| Offline RAG harness | **60/60 cases passed**; metrics are in `evals/results/feature-014-offline.json` |
| Retrieval ablation matrix | **5 configurations generated** in `evals/results/retrieval-ablations-v1.json` |
| Failed refresh safety | Day **1/7** recorded; active snapshot preserved |
| Corpus governance | Manifest, allowlist, provenance and demo/verified distinction covered by tests |

The seven-day acceptance criterion is intentionally still open. Days 2–7 require separate dated
executions of `evals/refresh_validation.py`; this record does not claim that those days occurred.
