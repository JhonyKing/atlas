# Feature 018 verification â€” 2026-08-08

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

No production Cron evidence, live LangSmith production trace, backup restore, rollback rehearsal,
or complete hosted functional smoke has been claimed. Those remain T031-T036.

## Follow-up verification (2026-08-10)

An MCP file-upload preview was verified as `READY` at
[`https://atlasai-hu543gtvg-jhonykings-projects.vercel.app`](https://atlasai-hu543gtvg-jhonykings-projects.vercel.app).
The build passed TypeScript and generated 12 static pages. This is a frontend-only preview;
it does not claim a managed API origin, hosted migrations, production Supabase, or a Git-connected
deployment. The UTF-8-preserving evidence is in
[`evals/results/vercel-preview-20260810-fixed-utf8.json`](../../evals/results/vercel-preview-20260810-fixed-utf8.json).

## Full local verification follow-up (2026-08-11)

- Frontend gates with Node 24: `pnpm lint` passed, `pnpm typecheck` passed, and Vitest passed
  **35/35 tests in 10 files**.
- Backend repository pytest: **423 passed, 4 skipped**; full Ruff passed; security regression
  **14/14**, deterministic evals **20/20**, portfolio checks **2/2**, and deployment secret scan
  passed.
- Deployment contract/readiness/release-evidence/secret-boundary tests: **7 passed**.
- Full backend mypy remains **not clean** with 33 pre-existing errors in eight non-agent modules
  (`comparison_cli`, news/ingestion typing, comparison/answer services, and missing YAML stubs).
- The deployment Playwright file could not start its configured Next web server within 60 seconds
  in this local harness, both in dev and production-server modes. No hosted smoke result is claimed;
  the existing local browser evidence remains valid where its manual Node 24 server was used.

## Integrated verification and web activation follow-up (2026-08-11)

- The integrated backend suite passed **428 tests with 4 skips**; full repository Ruff and strict
  mypy passed across 183 source files.
- Frontend Node 24 lint and typecheck passed; Vitest passed **35/35**; the full local Playwright run
  passed **149 tests with 4 intentional hosted-only skips**; the production build passed.
- The final explicit-locale and SVG-flag correction passed **5/5** focused AppShell journeys.
- Deployment contract/readiness/schema/security/integration follow-up passed **17/17** and
  `scripts/verify-deployment-secrets.ps1` passed.
- `apps/web/tests/e2e/deployment.spec.ts` now defines six real hosted journeys; TypeScript/ESLint
  pass and Playwright discovers all six. Their execution is intentionally tracked by T036.
- Vercel project `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` has READY preview/main and production
  deployments. The public web is [`https://atlasai-lilac.vercel.app`](https://atlasai-lilac.vercel.app).
- Supabase production `fcbclsaytbjpywlaplbh` is `ACTIVE_HEALTHY` on Postgres 17.6, with remote head
  `comparison_pricing_contract` and 33 hosted migration records. All 24 reviewed covering indexes are valid
  and ready; the hosted advisor reports zero unindexed foreign keys.

T005, T030 and T042 are closed. T031-T036 remain open because the paid isolated database targets,
production Cron activation/secrets, functional smoke, observability/restore and production rollback
evidence do not yet exist.

## Production access boundary follow-up (2026-08-11)

- Owner-authorized Vercel Authentication now protects preview deployments only.
- `atlasai-jhonykings-projects.vercel.app/en`, the URL already shared on LinkedIn, returns 200
  anonymously with ATLAS content and without `noindex`.
- The canonical and `main` production aliases also return 200 anonymously.
- Preview `atlasai-rjcxyvm0b-jhonykings-projects.vercel.app/en` still returns 302 to Vercel login.
- Evidence: `evals/results/vercel-production-access-20260811.json`.

This resolves public web access for recruiters. It does not close T032-T036 because production Cron,
secrets, functional research smoke, restore, and rollback evidence remain unavailable.

## Public web fail-closed verification (2026-08-11)

- Commit `174150ba53db8a98603fcc49e4262424f908a505` is `READY` in production deployment
  `dpl_GtVWDMyubQKuuKi2M3mNsKRiRr4T` and serves the primary domain.
- GitHub CI run [`31466909123`](https://github.com/JhonyKing/atlas/actions/runs/31466909123)
  passed all six jobs; Offline Evaluation run `31466909139` also passed.
- Frontend Vitest passed **38/38**; ESLint, strict TypeScript, and the production build passed.
- Hosted Playwright passed **2/2 executable web-only journeys**: explicit locales and SVG flags,
  every public feature route, bounded unavailable states, and zero requests to localhost.
- The browser now requires a configured public HTTPS `NEXT_PUBLIC_API_ORIGIN` in hosted builds.
  Authentication, private data, reviews, and governance also use that same origin.
- Four hosted functional journeys remain blocked, not failed: API health/readiness, cited
  answer/abstention, comparison/report generation, and corpus/news data. T032-T036 remain open.

## Managed worker wiring follow-up (2026-08-11)

- SpecKit Converge found that the declared worker command was not executable: the container
  entrypoint ignored role commands and `atlas-worker` deliberately raised a placeholder error.
- T044 replaced that placeholder with approved-manifest, PostgreSQL, bounded fetch, OpenAI
  embedding, retry-budget, queue-polling and graceful-shutdown wiring. `ATLAS_DATABASE_URL` now
  maps explicitly to the typed database setting used by the deployment templates.
- Focused configuration/deployment/ingestion verification passed **22/22** with Ruff and mypy
  clean.
- The complete backend regression suite then passed **434 tests with 4 intentional skips**;
  repository-wide Ruff and strict mypy passed across 183 source files.
- Docker built image
  `sha256:443d1bba82c306df09c369b0a8cab6b66a5a9147d08fdee1bb67517fcce41e76`.
  Running the image through its real entrypoint displayed the `atlas-worker` CLI, while a
  secret-free `--once` start exited non-zero with the controlled `OPENAI_API_KEY` requirement.
- T044 is closed. T032 remains open because the production Cron deployment, secret, and hosted
  collection-run observations have not been retained.

## Production API composition follow-up (2026-08-11)

- SpecKit Converge then found that the non-development app omitted `answer_service` and
  `operator_service`, so a future healthy container would still return 503 for cited answers and
  operator ingestion.
- New red contracts reproduced both defects and proved that `/readyz` incorrectly returned 200
  with `model_provider=disabled` in production.
- T045 now wires the verified cited-answer graph, durable operator queue and shared provider client
  before exposing the app. Preview/staging/production readiness requires the provider state to be
  `ready`.
- The focused contracts pass and the complete backend passes **436 tests with 4 intentional
  skips**; repository-wide Ruff and strict mypy remain clean across 183 source files.
- Docker image
  `sha256:bc1752b61a1b4e28ad3dacfea78aa6e01c096377cc96798a71f1fde578ca05a0`
  imports the corrected FastAPI runtime successfully with a deliberately unreachable local test
  DSN and no real secret values.
- T045 is closed. Hosted reachability and end-to-end behavior still require T032-T036.
