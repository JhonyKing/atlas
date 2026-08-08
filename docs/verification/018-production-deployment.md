# Feature 018 verification — 2026-08-08

## Completed repository evidence

- Backend: **377 passed, 4 skipped, 3 warnings** from the repository root.
- Deployment contract/readiness/release-evidence/managed-environment/rollback suites pass.
- Ruff passes for the changed backend, observability, deployment tests, and release scripts.
- Targeted mypy passes for changed deployment/config/health/pool/telemetry modules.
- `git diff --check` passes.
- `scripts/verify-deployment-secrets.ps1` passes while the local frontend dev process is running;
  the scanner ignores lock files and only inspects text artifact types.
- Frontend TypeScript and targeted ESLint pass using Node 24. Vitest passes **30 tests in 10
  files** when invoked with Node 24 directly; the default system Node 20 invocation fails with an
  ESM worker incompatibility, so CI must use the repository's Node 24 requirement.
- Docker image `atlas-api:deployment-contract` builds successfully from the repository root and
  imports `atlas` inside the resulting image; the first two build attempts exposed and fixed
  invalid lockfile/image-context assumptions.
- Local redacted evidence: `evals/results/release-evidence-local-20260808.json`.

## Intentionally not claimed

No Vercel project, public API URL, managed container, hosted migration, production Supabase
target, live LangSmith trace, backup restore, rollback rehearsal, or hosted bilingual smoke has
been claimed. Those require operator-owned credentials and are tracked as T030-T036. The
Playwright deployment file is a contract skeleton until `ATLAS_DEPLOYMENT_WEB_ORIGIN` is supplied.
