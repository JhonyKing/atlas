# Feature 001 quickstart baseline

| Scenario | Result |
|---|---:|
| Docker PostgreSQL health + Alembic head | passed locally |
| Health/corpus/abstention contracts | **10 passed** |
| Backend Ruff | passed |
| Frontend lint/typecheck | passed |
| Deterministic cited-answer evaluation | **46/46 passed**, `gpt-5.6-luna`, fixture mode |
| Five-person usability study | pending external participants (T074) |
| Seven-day refresh validation | pending days 2–7 (T075) |
| Full mypy gate | open baseline debt: 71 existing diagnostics; no claim of clean global typing |

The machine-readable evaluator artifact is `evals/results/001-cited-answer-baseline.json`. Fixture
evaluation is not live provider quality evidence.
