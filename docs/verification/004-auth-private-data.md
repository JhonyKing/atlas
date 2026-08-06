# Feature 004 verification record

Date: 2026-08-06  
Branch: `codex/004-optional-auth-private-data`

This record is the evidence required before closing the SpecKit tasks for optional authentication,
private-resource ownership, and safe uploads. Commands were executed from the repository root.

## Automated results

| Area | Command | Result |
|---|---|---|
| Auth/private regression | `apps/backend/.venv/Scripts/python.exe -m pytest apps/backend/tests/security apps/backend/tests/unit/auth apps/backend/tests/contract/auth apps/backend/tests/integration/auth apps/backend/tests/integration/security/test_cross_user_resources.py apps/backend/tests/integration/security/test_private_upload_pipeline.py -q` | **26 passed** |
| Convergence contracts | Account deletion, locale preference, and upload provenance contract tests | **40 auth/private tests passed** |
| Complete backend regression | `apps/backend/.venv/Scripts/python.exe -m pytest apps/backend/tests -q` | **225 passed, 4 skipped** |
| LangSmith sink privacy | `apps/backend/.venv/Scripts/python.exe -m pytest apps/backend/tests/unit/observability/test_langsmith.py -q` | **3 passed** |
| Auth latency target | `apps/backend/.venv/Scripts/python.exe -m pytest apps/backend/tests/load/test_auth_latency.py -q` | **100 login/renew/logout cycles under 3 seconds** |
| Python lint | `apps/backend/.venv/Scripts/python.exe -m ruff check ...` | **passed** |
| Python typing | `apps/backend/.venv/Scripts/python.exe -m mypy apps/backend/src/atlas/uploads apps/backend/src/atlas/privacy apps/backend/src/atlas/auth` | **no issues, 16 files** |
| Web lint | `pnpm --filter @atlas/web lint` | **passed** |
| Web typing | `pnpm --filter @atlas/web typecheck` | **passed** |
| Browser regression | `pnpm --filter @atlas/web test:e2e -- --project=chromium` | **18 passed** |

The browser run includes the three Feature 004 journeys (optional sign-in, rejected upload, safe
upload with cross-user empty history) and the existing answer, comparison, evidence, locale, and
report journeys.

## Database evidence

Docker container `atlas-ai-postgres-1` was healthy. Alembic applied migrations `0018_identity`,
`0019_private_data`, `0020_private_data_rls`, and `0021_private_upload_provenance` successfully.
The following SQL contracts were
executed with `psql -v ON_ERROR_STOP=1` and all completed without an exception:

- `database/tests/009_identity_rls.sql`: identity tables, RLS, and `current_subject_id()`.
- `database/tests/010_private_data_rls.sql`: private upload and deletion schema.
- `database/tests/011_cross_user_resources.sql`: ownership and upload policy presence.
- `database/tests/012_upload_quarantine.sql`: rejected uploads have no searchable chunks.

The database was empty for private uploads during this run, so the quarantine aggregate returned
zero rows; the contract still checks the invariant and fails if a rejected upload has chunks.

## LangSmith and redaction review

The local environment reports `LANGSMITH_TRACING=true`, a configured API key, and project
`atlas-ai` (the key itself is not printed or stored in this document). `LangSmithTraceSink` creates
runs with `hide_inputs=True` and `hide_outputs=True`. Both start and end metadata pass through the
content-free scalar allowlist; fields containing question, evidence, content, cookie,
authorization, secret, or raw values are omitted. The unit test also attempts to send a
`private_content` field and verifies it is absent from the update payload.

Auth/private regression tests additionally verify that raw session tokens, passwords, visitor
identifiers, resource identifiers for foreign users, and private upload bytes do not appear in
observable error or trace representations.

## Reproduction

See `specs/004-optional-auth-private-data/quickstart.md` for the complete command sequence. The
quickstart assumes Docker Desktop is running and uses only local deterministic adapters; no hosted
auth or malware-scanner credential is needed for the tests.
