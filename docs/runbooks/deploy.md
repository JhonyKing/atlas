# Deployment runbook

1. Build from an immutable commit or release tag.
2. Run all CI gates, including deterministic RAG evals and secret scanning.
3. Run `scripts/release-migrate.ps1 -DryRun`, then apply the forward-only migration in the target.
4. Deploy the API/worker image and Vercel web with environment-scoped secrets.
5. Wait for `/healthz` and `/readyz`; run `scripts/deployment-smoke.py`.
6. Attach the redacted release evidence artifact to the release. Never paste secrets into logs.

For Vercel, set the project **Root Directory** to `apps/web`. If the project is temporarily
configured at the repository root, the root `vercel.json` provides the same build command and
points at `apps/web/.next`; this is a compatibility fallback, not a replacement for the correct
Root Directory setting. The GitHub environment must provide `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and
the environment-specific project ID (`VERCEL_PREVIEW_PROJECT_ID` or
`VERCEL_PRODUCTION_PROJECT_ID`). The workflow links the project explicitly before deploying;
there is no dependency on a developer's local `.vercel` directory.
