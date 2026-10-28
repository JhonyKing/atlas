# Quickstart Validation: Technology Comparator

## Prerequisites

- Docker PostgreSQL is running and the verified corpus snapshot is available.
- Backend dependencies are installed in `apps/backend/.venv`.
- Node 24 and pnpm are available for the web checks.

## 1. Start infrastructure and migrate

```powershell
docker compose up -d postgres
$env:ATLAS_DATABASE_URL="postgresql+psycopg://atlas:atlas-local-only@localhost:55432/atlas"
apps\backend\.venv\Scripts\python.exe -m alembic -c database\alembic.ini upgrade head
```

## 2. Start API and web application

Use the existing local API on `http://127.0.0.1:8000` and web app on `http://127.0.0.1:3000`, or
start them with the commands in [001-cited-answer/quickstart.md](../001-cited-answer/quickstart.md).

Verify the API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
Invoke-RestMethod http://127.0.0.1:8000/v1/corpus
```

## 3. Compare two technologies

Submit a request with two supported technology IDs and at least three criteria. The UI or API must
show progress, a matrix, and evidence on every populated cell.

Expected behavior:

- Two rows are present and criteria are explicit columns.
- Each supported cell opens canonical source metadata and an excerpt.
- Unsupported and contradictory cells explain their state instead of inventing a value.
- Repeating the same idempotency key returns the same run and does not consume another quota unit.

## 4. Validate four technologies, cancellation and invalid input

Repeat with four technologies, cancel a running comparison, submit one technology, duplicate
technologies, and an empty criteria list. Invalid requests preserve selections and return a useful
correction without retrieval or model calls.

## 5. Validate bilingual parity

Run one comparison at `/en/compare` and the same request at `/es/compare`. Confirm that locale
changes translate controls and status text while technology IDs, criterion IDs, cell states,
evidence IDs, dates, versions and numeric values remain identical.

For a price comparison, verify that ATLAS routes retrieval to `pricing` sources only. Technical
documentation is never authoritative for a price claim. LangGraph and LangChain render
`not_applicable` (`No aplica` in Spanish); a provider without a reviewed pricing page renders
`unsupported` (`Sin evidencia`). Expand a populated cell and verify title, publisher, bounded
excerpt, capture date, version and canonical URL before using its value.

## 6. Run quality gates

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests -q
apps\backend\.venv\Scripts\python.exe -m ruff check apps/backend/src/atlas apps/backend/tests
pnpm --filter @atlas/web lint
pnpm --filter @atlas/web typecheck
pnpm --filter @atlas/web test
pnpm --filter @atlas/web test:e2e
```

The comparison dataset and evaluation report must record the corpus snapshot, application commit,
locale and retrieval version.
