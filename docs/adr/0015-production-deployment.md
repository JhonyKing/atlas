# ADR 0015: Separate web, API/worker, and managed data deployment

## Decision

Deploy the Next.js web to Vercel, run FastAPI and the ingestion worker in a managed container
runtime, and use Supabase for managed Postgres/Auth/Storage/pgvector. Apply the checked-in
Alembic head before declaring `/readyz` healthy. Preview and production are isolated.

The first managed runtime adapter is Fly.io: one application, separate `api` and `worker` process
groups, an explicit Alembic release command, two API machines, and one worker machine. The
provider-neutral manifest remains the architectural contract; `infra/deployment/fly.toml` is the
deployable edge configuration.

## Consequences

This keeps long-running agent, ingestion, and export work out of serverless request limits and
makes migration, rollback, worker health, and evidence gates explicit. A real deployment is not
claimed until operator-owned provider IDs, secrets, smoke results, backup/restore, and rollback
evidence are recorded.
