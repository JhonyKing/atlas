# Runbook: local development

## Start dependencies

From `C:\Users\Usuario\Documents\ATLAS IA`:

```powershell
docker compose up -d --wait postgres
$env:ATLAS_DATABASE_URL = "postgresql+psycopg://atlas:atlas-local-only@localhost:55432/atlas"
apps\backend\.venv\Scripts\python.exe -m alembic -c database\alembic.ini upgrade head
```

The local image exposes PostgreSQL on `55432`; do not assume port `5432` on Windows.

## Run services

```powershell
Start-Process -WindowStyle Hidden -FilePath ".\apps\backend\.venv\Scripts\python.exe" -ArgumentList "-m","uvicorn","atlas.api.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory ".\apps\backend"
pnpm --filter @atlas/web dev
```

Check process and dependency readiness:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/healthz | Select-Object -ExpandProperty Content
Invoke-WebRequest http://127.0.0.1:8000/v1/corpus | Select-Object -ExpandProperty Content
```

`healthz` means the process is alive and whether its required database probe is ready; it is not a
business answer endpoint.

## Quality gates

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests -q --basetemp C:\tmp\atlas-pytest
apps\backend\.venv\Scripts\ruff.exe check apps/backend/src apps/backend/tests
apps\backend\.venv\Scripts\mypy.exe apps/backend/src
pnpm --filter @atlas/web typecheck
pnpm --filter @atlas/web lint
pnpm --filter @atlas/web exec playwright test --workers=1
apps\backend\.venv\Scripts\python.exe -m atlas.evaluation.cli run --dataset evals/datasets/cited-answer-v1.jsonl
```

Vitest requires the Node 24 toolchain pinned by CI; on the current Node 20 machine it may fail
before collection with `ERR_REQUIRE_ESM` from jsdom dependencies.
