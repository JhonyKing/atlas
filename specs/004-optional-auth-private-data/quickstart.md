# Feature 004 Quickstart

## Prerequisites

- Docker PostgreSQL is running.
- Backend and web dependencies are installed.
- No hosted-auth or malware-scanner secret is required for deterministic tests.

## Contract and security tests

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/contract/auth -q
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/integration/security -q
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/security -q
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/load/test_auth_latency.py -q
```

## Database policy checks

```powershell
apps\backend\.venv\Scripts\alembic.exe -c database/alembic.ini upgrade head
Get-Content database/tests/009_identity_rls.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
Get-Content database/tests/010_private_data_rls.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
Get-Content database/tests/011_cross_user_resources.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
Get-Content database/tests/012_upload_quarantine.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
```

The database checks must prove that a second subject cannot read, download, update, or delete a
thread, report, artifact, feedback item, or upload owned by the first subject.

## Browser journeys

Run the anonymous, sign-in, session-renewal, private-upload, foreign-owner, and account-deletion
Playwright journeys. The anonymous journey must pass without a sign-in prompt.

```powershell
pnpm --filter @atlas/web lint
pnpm --filter @atlas/web typecheck
pnpm --filter @atlas/web test:e2e -- --project=chromium
```

The browser suite currently includes the three Feature 004 journeys plus the existing regression
journeys. It should finish with 18 passing tests.

## Expected result

- Anonymous quota and existing answer/comparison journeys remain unchanged.
- Protected resources return safe not-found semantics across owners.
- Unsafe uploads never become searchable data.
- Account and upload deletion are repeat-safe and produce a non-sensitive audit outcome.
