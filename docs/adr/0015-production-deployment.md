# ADR 0015: Separate web, API/worker, and managed data deployment

## Decision

The original container-first decision below is retained as historical context. The 2026-08-13
amendment at the end of this ADR supersedes it for the owner-approved beta.

Deploy the Next.js web to Vercel, run FastAPI and the ingestion worker in a managed container
runtime, and use Supabase for managed Postgres/Auth/Storage/pgvector. Apply the checked-in
Alembic head before declaring `/readyz` healthy. Preview and production are isolated.

The owner approved an interim portfolio beta on the existing Vercel Hobby account. The API's
cited-answer HTTP surface may run as a Vercel Python Function while the full managed API/worker
runtime remains open. This bounded adapter does not replace the long-running worker decision or
close Feature 018.

## 2026-08-13 amendment: scheduled beta path

The owner subsequently approved the lower-cost beta path: Vercel hosts the API and five bounded
per-collection Cron routes, while Supabase provides the durable queue and database. The checked-in
portable worker remains useful for local or alternative-runtime execution, but no always-on managed
worker is required for beta. Feature 018 remains open only for production Cron/secrets activation,
hosted smoke, observability, backup/restore, rollback, and release evidence.

## Consequences

This keeps long-running agent, ingestion, and export work out of serverless request limits and
makes migration, rollback, worker health, and evidence gates explicit. A real deployment is not
claimed until operator-owned provider IDs, secrets, smoke results, backup/restore, and rollback
evidence are recorded.
