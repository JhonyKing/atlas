# Production Deployment Validation Quickstart

This guide validates the deployment feature. It is not a claim that a production environment is
already provisioned.

## Prerequisites

- A Vercel project for `apps/web`.
- A Supabase project with a separate preview/staging target.
- A Vercel production project with Cron enabled for `apps/backend`.
- Environment-scoped secrets supplied through the platform secret managers.
- A domain and auth redirect URLs controlled by the operator.

## Repository gates

From the repository root:

```powershell
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
```

From `apps/backend`:

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m pytest -m contract
```

Run the deterministic evaluation gate and inspect its execution mode before treating it as a
quality signal. Live provider/LangSmith evaluation remains a separate evidence step.

## Environment validation

1. Apply migrations to the isolated Supabase target and record the head revision.
2. Build the API function and record the immutable Vercel deployment identifier.
3. Configure the API origin in Vercel as `NEXT_PUBLIC_API_ORIGIN` for the matching environment.
4. Configure `CRON_SECRET`, CORS, auth callbacks, model provider, LangSmith, storage, and database secrets in the
   server-side secret managers only.
5. Run the deployment readiness contract at `GET /healthz` and `GET /readyz`.
6. Invoke each collection-scoped Cron route once with the platform-provided secret, verify one
   bounded durable run per collection, and save its redacted JSON result.
7. Run the smoke contract and save its redacted JSON result as a release evidence bundle.
8. Open the Vercel URL in a clean browser, test `/` and locale selection, and record the URL,
   build ID, source revision, and timestamp.

## Rollback validation

- Deploy a known-good application revision in a non-production environment.
- Introduce a controlled health failure and verify traffic is not promoted.
- Restore the previous application version without automatically reversing applied migrations.
- Re-run readiness and smoke tests; retain both the failed and recovered evidence bundles.

## Evidence required to close the feature

- Public web URL and API URL (not localhost).
- Vercel build/deployment ID and API image digest.
- Supabase project/environment identifier with redacted configuration evidence.
- Migration head and restore-verification evidence.
- Passing required CI/release checks.
- Passing bilingual smoke results and release evidence bundle.
- Observability trace/log links with redaction verified.
- Rollback and incident-runbook rehearsal results.
