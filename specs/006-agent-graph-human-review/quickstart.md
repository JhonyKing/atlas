# Feature 006 Quickstart

Deterministic checks will run without provider keys:

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/agent apps/backend/tests/contract/agent apps/backend/tests/integration/agent apps/backend/tests/security/test_agent_orchestration.py -q
apps\backend\.venv\Scripts\python.exe -m ruff check apps/backend/src/atlas/agent apps/backend/src/atlas/api/routes/agent.py
apps\backend\.venv\Scripts\python.exe -m mypy apps/backend/src/atlas/agent
```

With Docker PostgreSQL running:

```powershell
apps\backend\.venv\Scripts\alembic.exe -c database/alembic.ini upgrade head
Get-Content database/tests/014_agent_checkpoints_reviews.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
```

The browser journey must show a review-required result, reject unauthorized/expired decisions,
accept one approved edit, and prove that a resumed thread does not duplicate publication.
