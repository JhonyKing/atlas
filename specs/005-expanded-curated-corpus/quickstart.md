# Feature 005 Quickstart

## Prerequisites

- Python and web dependencies are installed.
- Docker PostgreSQL is running for migration/SQL checks.
- No live provider key is needed for deterministic fixture tests.

## Deterministic checks

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/ingestion apps/backend/tests/contract/ingestion apps/backend/tests/integration/ingestion apps/backend/tests/security/test_ingestion_governance.py -q
apps\backend\.venv\Scripts\python.exe -m ruff check apps/backend/src/atlas/ingestion apps/backend/src/atlas/api/routes/governance.py
apps\backend\.venv\Scripts\python.exe -m mypy apps/backend/src/atlas/ingestion/catalog.py apps/backend/src/atlas/ingestion/governance.py apps/backend/src/atlas/ingestion/connectors/registry.py apps/backend/src/atlas/ingestion/connectors/github_releases.py apps/backend/src/atlas/ingestion/connectors/scholarly.py apps/backend/src/atlas/ingestion/connectors/pricing_snapshots.py apps/backend/src/atlas/ingestion/connectors/private_content.py apps/backend/src/atlas/ingestion/normalizer.py apps/backend/src/atlas/observability/events.py
```

## Database checks

```powershell
apps\backend\.venv\Scripts\alembic.exe -c database/alembic.ini upgrade head
Get-Content database/tests/013_ingestion_governance.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
```

## Browser/operator check

```powershell
pnpm --filter @atlas/web lint
pnpm --filter @atlas/web typecheck
pnpm --filter @atlas/web test:e2e -- --project=chromium tests/e2e/ingestion-governance.spec.ts
```

Expected result: the governance panel shows approved/disabled collections, freshness, retries,
dead letters, and the seven-day target without exposing source bodies or private tenant content.

One-command verification (migration and browser checks included):

```powershell
pnpm test:ingestion
```
