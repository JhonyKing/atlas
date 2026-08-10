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
