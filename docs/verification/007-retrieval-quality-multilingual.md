# Feature 007 — retrieval quality and multilingual evidence

## Scope

This slice adds bounded query rewriting, typed retrieval filters, deterministic deduplication and
source diversity, a hard context budget, multilingual metadata/fallback behavior, and an optional
reranker decision gate. The baseline remains the default unless paired metrics approve a candidate.

## Verification evidence

| Check | Result |
|---|---:|
| Targeted retrieval/security tests | 10 passed |
| Full backend regression | 275 passed, 4 skipped |
| Ruff (retrieval package and tests) | passed |
| mypy (retrieval package) | passed |
| Retrieval JSONL cases | 4 cases |
| Baseline Hit@5 / MRR | 1.0 / 1.0 |
| Candidate Hit@5 / MRR | 1.0 / 1.0 |
| Baseline/candidate context precision | 0.5 / 0.5 |
| Baseline/candidate context recall | 1.0 / 1.0 |
| Baseline/candidate citation precision | 0.5 / 0.5 |
| Freshness accuracy | 1.0 |

Commands from repository root:

```powershell
pnpm test:retrieval
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests -q
apps\backend\.venv\Scripts\python.exe -m atlas.evaluation.retrieval_quality `
  --dataset evals/cases/007-retrieval-quality-multilingual.jsonl `
  --output docs/verification/007-retrieval-quality-multilingual-metrics.json
```

The dataset intentionally contains deterministic fixture IDs only; it does not claim live corpus
quality. Production reranker enablement still requires a paired benchmark with measured latency
and cost.
