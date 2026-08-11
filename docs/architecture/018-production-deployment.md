# Feature 018 — production deployment architecture

ATLAS uses three separately deployable surfaces:

1. Next.js web on Vercel, with preview and production projects separated.
2. FastAPI API and ingestion worker in a managed container runtime. They are not Vercel
   serverless functions and use immutable image digests.
3. Supabase Postgres/Auth/Storage/pgvector with pooled connections and forward-only Alembic
   migrations applied before API readiness.

The browser receives only `NEXT_PUBLIC_API_ORIGIN`. Provider credentials, database URLs,
operator tokens, and LangSmith credentials are platform secrets. Production rejects localhost
origins and missing required secrets. `/healthz` is liveness; `/readyz` is the dependency gate.

Preview and production use separate Vercel projects, database targets, storage buckets, auth
redirects, LangSmith projects, and quotas. Live provider/LangSmith checks are evidence from the
deployed environment; deterministic RAG evaluations remain a mandatory CI/release gate.

## API and worker process boundary

The backend image has one default API process and an explicit worker command. With no arguments,
`/entrypoint.sh` starts Uvicorn; when the managed worker role supplies `atlas-worker`, the
entrypoint dispatches that command instead of accidentally starting a second API. The image
packages the reviewed corpus manifests alongside all database migrations.

`atlas-worker` loads only an approved manifest, accepts `DATABASE_URL` or the deployment-facing
`ATLAS_DATABASE_URL`, requires the OpenAI secret, and constructs the PostgreSQL repository,
allowlisted fetcher, and embedding adapter inside the process. It drains a bounded number of
durable ingestion jobs per cycle, waits interruptibly when idle, and handles termination signals
before closing HTTP/provider/database resources. The managed runtime remains unprovisioned; this
section records deployable repository wiring, not hosted evidence.

The non-development FastAPI composition also fails closed. It requires provider and visitor
secrets, a verified corpus snapshot, a constructible cited-answer graph, durable agent
repositories, and a durable ingestion enqueue/status service. Only after those dependencies are
constructed does the app expose the answer/operator services and report `model_provider=ready`.
For preview, staging and production, `/readyz` returns non-2xx when that provider state is not
ready; a healthy database alone is no longer sufficient to accept traffic.
