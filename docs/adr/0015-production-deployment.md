# ADR 0015: Separate web, API/worker, and managed data deployment

## Decision

Deploy the Next.js web and collection-scoped scheduled ingestion routes to Vercel, and use Supabase
for managed Postgres/Auth/Storage/pgvector plus the durable ingestion queue. The existing FastAPI
`atlas-worker` remains the portable local/container implementation, but the approved portfolio beta
does not require an always-on worker runtime. Apply the checked-in Alembic head before declaring
`/readyz` healthy. Preview and production are isolated.

The owner approved an interim portfolio beta on the existing Vercel Hobby account. The API's
cited-answer HTTP surface and collection-scoped Cron routes may run as Vercel Python Functions
while hosted Cron evidence remains open. The portable worker seam remains available for a future
scale-out decision; this bounded adapter does not close Feature 018 by itself.

## Consequences

Daily ingestion is bounded to one collection and one durable queue run per authenticated Cron
invocation, keeping the Hobby beta free of an idle worker bill while preserving idempotency,
last-good promotion and auditable run state. A real deployment is not claimed until operator-owned
provider IDs, secrets, smoke results, backup/restore, and rollback evidence are recorded. If a
collection outgrows the function limit, the queue/worker seam can later be moved to a managed
container without changing the corpus contract.
