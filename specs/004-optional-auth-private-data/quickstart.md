# Feature 004 Quickstart

## Prerequisites

- Docker PostgreSQL is running.
- Backend and web dependencies are installed.
- No hosted-auth or malware-scanner secret is required for deterministic tests.

## Contract and security tests

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/contract/auth -q
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/integration/security -q
```

## Database policy checks

```powershell
apps\backend\.venv\Scripts\alembic.exe -c database/alembic.ini upgrade head
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/database -q
```

The database checks must prove that a second subject cannot read, download, update, or delete a
thread, report, artifact, feedback item, or upload owned by the first subject.

## Browser journeys

Run the anonymous, sign-in, session-renewal, private-upload, foreign-owner, and account-deletion
Playwright journeys. The anonymous journey must pass without a sign-in prompt.

## Expected result

- Anonymous quota and existing answer/comparison journeys remain unchanged.
- Protected resources return safe not-found semantics across owners.
- Unsafe uploads never become searchable data.
- Account and upload deletion are repeat-safe and produce a non-sensitive audit outcome.

