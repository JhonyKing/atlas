# Feature 005 verification evidence

Feature branch: `codex/005-expanded-curated-corpus`

| Check | Result |
|---|---:|
| Feature 005 backend unit/contract/integration/security suite | **43 passed, 3 skipped** |
| Full backend regression (`apps/backend/tests`) | **242 passed, 4 skipped** |
| New ingestion modules Ruff | **passed** |
| New ingestion/observability modules mypy | **passed (9 files)** |
| Web lint | **passed** |
| Web typecheck | **passed** |
| Playwright Chromium suite | **19 passed** |
| Alembic migration `0022_ingestion_governance` | **applied** |
| SQL contract `database/tests/013_ingestion_governance.sql` | **passed** |

The browser journey verifies the Spanish governance panel and aggregate collection coverage. The
deterministic fixtures verify all 16 catalog entries, allowlist rejection, changed/unchanged
versions, seven-day coverage metadata, policy disablement, takedown, retries/dead letter, private
tenant isolation and redacted telemetry. No live provider key is required.
