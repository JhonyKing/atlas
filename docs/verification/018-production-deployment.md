# Feature 018 verification — 2026-08-08

## Completed repository evidence

- Backend: **377 passed, 4 skipped, 3 warnings** from the repository root.
- Deployment contract/readiness/release-evidence/managed-environment/rollback suites pass.
- Managed-environment contract fixtures now cover the migration head, RLS/private SQL contracts,
  no-localhost pool boundary, and distinct preview/production templates.
- Ruff passes for the changed backend, observability, deployment tests, and release scripts.
- Targeted mypy passes for changed deployment/config/health/pool/telemetry modules.
- `git diff --check` passes.
- `scripts/verify-deployment-secrets.ps1` passes while the local frontend dev process is running;
  the scanner ignores lock files and only inspects text artifact types.
- Frontend TypeScript and targeted ESLint pass using Node 24. Vitest passes **30 tests in 10
  files** when invoked with Node 24 directly; the default system Node 20 invocation fails with an
  ESM worker incompatibility, so CI must use the repository's Node 24 requirement.
- Deployment Playwright contract parses successfully with four intentional skips when no hosted
  origin is configured; it will execute only after `ATLAS_DEPLOYMENT_WEB_ORIGIN` is supplied.
- Docker image `atlas-api:deployment-contract` builds successfully from the repository root and
  imports `atlas` inside the resulting image; the first two build attempts exposed and fixed
  invalid lockfile/image-context assumptions.
- Local redacted evidence: `evals/results/release-evidence-local-20260808.json`.

## Intentionally not claimed

No Vercel project, public API URL, managed container, hosted migration, production Supabase
target, live LangSmith trace, backup restore, rollback rehearsal, or hosted bilingual smoke has
been claimed. Those require operator-owned credentials and are tracked as T030-T036. The
Playwright deployment file is a contract skeleton until `ATLAS_DEPLOYMENT_WEB_ORIGIN` is supplied.

## Follow-up verification (2026-08-10)

An MCP file-upload preview was verified as `READY` at
[`https://atlasai-hu543gtvg-jhonykings-projects.vercel.app`](https://atlasai-hu543gtvg-jhonykings-projects.vercel.app).
The build passed TypeScript and generated 12 static pages. This is a frontend-only preview;
it does not claim a managed API origin, hosted migrations, production Supabase, or a Git-connected
deployment. The UTF-8-preserving evidence is in
[`evals/results/vercel-preview-20260810-fixed-utf8.json`](../../evals/results/vercel-preview-20260810-fixed-utf8.json).
