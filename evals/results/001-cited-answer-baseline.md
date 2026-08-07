# Feature 001 quickstart baseline

| Scenario | Result |
|---|---:|
| Docker PostgreSQL health + Alembic head | passed locally |
| Health/corpus/abstention contracts | **10 passed** |
| Abstention, prompt-injection and quota quickstart checks | **16 passed** |
| Backend Ruff | passed |
| Frontend lint/typecheck | passed |
| Deterministic cited-answer evaluation | **46/46 passed**, `gpt-5.6-luna`, fixture mode |
| Five-person usability study | pending external participants (T074) |
| Seven-day refresh validation | pending days 2–7 (T075) |
| Full mypy gate | Feature 017 later closed the repository-wide gate; this historical branch baseline predates that closure |

The machine-readable evaluator artifact is `evals/results/001-cited-answer-baseline.json`. Fixture
evaluation is not live provider quality evidence.
The refreshed local fixture artifact is `evals/results/001-cited-answer-baseline-20260807.json` and
records **60/60** cases passed. External usability and seven-day refresh evidence remain open.
