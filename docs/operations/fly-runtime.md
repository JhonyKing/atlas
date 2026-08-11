# Fly.io managed runtime runbook

## Current status

The repository is ready to deploy the ATLAS FastAPI API and ingestion worker to Fly.io, but no
billable Fly application has been created. This document is preparation evidence, not a production
claim. The Vercel web application and Supabase production database already exist; the missing
managed API/worker keeps Feature 018 T032-T036 open.

## Selected production shape

- Region: `dfw`, close to the current operator and the Supabase US West project.
- API: two `shared-cpu-1x` machines with 1 GiB RAM each.
- Worker: one `shared-cpu-1x` machine with 1 GiB RAM.
- Image: `infra/containers/backend/Dockerfile` built remotely from the repository.
- Migration: `alembic -c database/alembic.ini upgrade head` runs once as the release command.
- Public traffic: Fly HTTPS routes only to the `api` process on port 8000.
- Readiness: Fly checks `GET /readyz`; the image also exposes `GET /healthz`.

At Fly.io's published North America price on 2026-08-11, three continuously running 1 GiB
`shared-cpu-1x` machines cost approximately USD 17.76/month before network egress. Billing remains
the owner's explicit decision. The source is Fly.io's current
[resource-pricing table](https://fly.io/docs/about/pricing/); process-specific configuration is
documented in Fly.io's [application configuration reference](https://fly.io/docs/reference/configuration/).

## One-time operator boundary

The owner must complete only the account boundary that Codex cannot perform on their behalf:

1. Create or sign in to a Fly.io account.
2. Add a payment method and approve the expected monthly spend.
3. Authenticate `flyctl` through the browser when Codex starts the login flow.
4. Put the Supabase pooled production connection string in the local `.env` as
   `ATLAS_DATABASE_URL`; do not paste it into chat or commit it.

The current local `.env` contains a local Docker `DATABASE_URL`, not the Supabase production pooler
URL, and does not contain values for `ATLAS_VISITOR_HMAC_SECRET` or `ATLAS_OPERATOR_TOKEN`. These
must be created locally before deployment. Existing OpenAI and LangSmith key presence is checked by
name only; their values must never be printed or committed.

## Deployment sequence after authentication

Run from the repository root. Replace `<fly-app>` and `<fly-org>` with the non-secret identifiers
chosen in the Fly account.

```powershell
flyctl apps create <fly-app> --org <fly-org>
flyctl deploy --app <fly-app> --config infra/deployment/fly.toml --remote-only
flyctl scale count api=2 worker=1 --app <fly-app> --yes
flyctl status --app <fly-app>
```

Secrets must be imported through standard input or the Fly dashboard, never written as command
arguments. Required server-only names are:

- `ATLAS_DATABASE_URL`
- `OPENAI_API_KEY`
- `ATLAS_VISITOR_HMAC_SECRET`
- `ATLAS_OPERATOR_TOKEN`
- `LANGSMITH_API_KEY`

Environment-scoped non-secret values include `WEB_ORIGIN`, `API_ORIGIN`, `LANGSMITH_PROJECT`,
`LANGSMITH_TRACING`, model IDs, corpus manifest, and bounded worker settings. After the Fly domain
exists, set the same HTTPS API origin as Vercel's `NEXT_PUBLIC_API_ORIGIN`, restrict CORS to the
production Vercel origins, and redeploy the web application.

## Evidence required before closing T032

- Fly application and organization identifiers (non-secret).
- HTTPS API URL returning `/healthz` and `/readyz` according to contract.
- Immutable built image digest and Fly deployment/release ID.
- Two healthy API machines and one healthy worker machine.
- Successful migration release against Supabase production.
- Redacted logs proving no credential or private document content is emitted.

T033-T036 start only after this evidence exists; they configure the environment, execute the
quickstart, verify operations, and run the complete bilingual production smoke suite.
