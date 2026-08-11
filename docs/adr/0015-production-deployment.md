# ADR 0015: Separate web, API/worker, and managed data deployment

## Decision

Deploy the Next.js web to Vercel, run FastAPI and the ingestion worker in a managed container
runtime, and use Supabase for managed Postgres/Auth/Storage/pgvector. Apply the checked-in
Alembic head before declaring `/readyz` healthy. Preview and production are isolated.

## Consequences

This keeps long-running agent, ingestion, and export work out of serverless request limits and
makes migration, rollback, worker health, and evidence gates explicit. A real deployment is not
claimed until operator-owned provider IDs, secrets, smoke results, backup/restore, and rollback
evidence are recorded.
