# Feature 007 Quickstart

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/retrieval apps/backend/tests/integration/retrieval apps/backend/tests/security/test_retrieval_quality.py -q
apps\backend\.venv\Scripts\python.exe -m ruff check apps/backend/src/atlas/retrieval
apps\backend\.venv\Scripts\python.exe -m mypy apps/backend/src/atlas/retrieval
```

The deterministic eval cases are in `evals/cases/007-retrieval-quality-multilingual.jsonl`.
Expected behavior: original queries remain available, filters are explicit, duplicate context is
removed, evidence stays within budget, and the baseline remains active when a reranker has no
measured improvement.
