# Feature 006 verification evidence

Branch: `codex/006-agent-graph-human-review`

| Check | Result |
|---|---:|
| Agent unit/contract/security suite | **25 passed** |
| Full backend regression before latest API/UI slice | **253 passed, 4 skipped** |
| Agent Ruff | **passed** |
| Agent/API mypy | **passed (8 files)** |
| Web lint and typecheck | **passed** |
| Human-review Playwright journey | **1 passed** |
| Full Chromium coverage including review journey | **20 passed** (19 existing + 1 review) |
| Alembic migration 0024 and SQL contract 014 | **passed** |

The deterministic evidence covers factual/comparison/report/abstention/cancellation routes,
redacted node events, checkpoint integrity/expiry/single-use replay, reviewer authorization and
expiry, publication gating, bilingual review UI, and safe status/resume API responses.
