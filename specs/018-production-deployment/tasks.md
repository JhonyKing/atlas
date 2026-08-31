# Tasks: Production Deployment

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/)

**Prerequisites**: Feature 017 CI/CD hardening remains green. No task below implies that a real
Vercel, Supabase, or managed-container account already exists.

## Phase 1: Contracts and failing validation (P1)

- [X] T001 [US3] Add contract tests for environment-scoped origins, secret names, and preview/production separation in `apps/backend/tests/contract/test_deployment_config.py` and `apps/web/src/lib/env.test.ts`.
- [X] T002 [US3] Add readiness contract tests for `/healthz` and `/readyz`, including truthful database/migration/provider failure categories, in `apps/backend/tests/contract/test_readiness.py`.
- [X] T003 [US3] Add JSON-schema validation tests for `specs/018-production-deployment/contracts/release-evidence.schema.json` in `apps/backend/tests/contract/test_release_evidence_schema.py`.
- [X] T004 [US3] Add a failing secret-boundary test that scans browser bundles, logs, traces, and evidence artifacts for prohibited keys in `scripts/verify-deployment-secrets.ps1` and `apps/backend/tests/security/test_deployment_secret_boundary.py`.
- [X] T005 [US1] Add Playwright smoke journeys for deployed root/locale, API origin, Spanish labels, cited-answer/abstention, comparison, report, news, and corpus status in `apps/web/tests/e2e/deployment.spec.ts`. (Evidence: six hosted journeys reject localhost requests, assert both explicit locales and flag assets, verify readiness, exercise answer/abstention, comparison/report artifacts, corpus and news. On deployment `dpl_GtVWDMyubQKuuKi2M3mNsKRiRr4T`, both executable web-only journeys passed; four API-dependent journeys remain T036.)
- [X] T006 [US2] Add backend smoke contract fixtures for Supabase-like migration head, RLS ownership, private deletion, connection failure, and no-localhost fallback in `apps/backend/tests/integration/deployment/test_managed_environment.py`. Local contract fixtures pass; live managed-data execution remains T031/T034.

## Phase 2: Environment and runtime foundation (P1)

- [X] T007 [US3] Define typed environment schemas and fail-closed validation for preview/staging/production in `apps/backend/src/atlas/config.py` and `apps/web/src/lib/env.ts`.
- [X] T008 [P] [US1] Configure Vercel project build, preview/production variables, Node/pnpm versions, security headers, and exact API origin in `apps/web/vercel.json` and `apps/web/README.md`.
- [X] T009 [P] [US2] Add a production-ready API/worker container definition with non-root user, pinned dependencies, startup command, and healthcheck in `infra/containers/backend/Dockerfile` and `infra/containers/backend/entrypoint.sh`.
- [X] T010 [P] [US2] Add provider-neutral managed-container deployment manifest with web/API/worker roles, resource bounds, HTTPS, health checks, and immutable image references in `infra/deployment/api-worker.yaml`.
- [X] T011 [US2] Add environment templates with placeholders only and document required operator secrets in `.env.example`, `infra/env/preview.example`, and `infra/env/production.example`.
- [X] T012 [US3] Add CORS, auth callback, storage, model-provider, and LangSmith environment contract documentation in `docs/architecture/018-production-deployment.md`.

## Phase 3: Supabase data/auth/storage integration (P1)

- [X] T013 [US2] Add a Supabase connection/pooling adapter behind existing persistence ports in `apps/backend/src/atlas/persistence/` without leaking provider SDK types into domain contracts.
- [X] T014 [US2] Add migration preflight and forward-only release command that verifies the expected Alembic head and refuses unsafe drift in `scripts/release-migrate.ps1` and `apps/backend/tests/integration/deployment/test_migration_release.py`.
- [X] T015 [US2] Add Supabase-compatible RLS, storage, auth, and private-resource policy checks to the existing database contract suite in `database/tests/`.
- [X] T016 [US2] Add isolated test-tenant setup/teardown and ownership/deletion smoke checks in `scripts/deployment-test-tenant.ps1`.
- [X] T017 [US2] Add backup/restore verification procedure and evidence capture for a non-production Supabase target in `scripts/verify-backup-restore.ps1` and `docs/runbooks/backup-restore.md`.

## Phase 4: Release pipeline and evidence (P1)

- [X] T018 [US3] Extend `.github/workflows/ci.yml` with deployment configuration validation, secret scanning, release-evidence schema validation, and required artifact upload.
- [X] T019 [US3] Add `.github/workflows/deploy-preview.yml` with Vercel preview deployment, isolated API target, migration dry-run, readiness check, smoke suite, and redacted evidence artifact.
- [X] T020 [US3] Add `.github/workflows/deploy-production.yml` with explicit approval, immutable web/API versions, forward migration step, health/readiness gates, smoke suite, and promotion/rollback behavior.
- [X] T021 [US3] Implement release evidence generation and redaction in `scripts/generate-release-evidence.py` with source revision, web build, image digest, migration head, corpus/model/locale versions, checks, and timestamps.
- [X] T022 [US3] Add deterministic deployment smoke runner in `scripts/deployment-smoke.py` that validates the contract in `specs/018-production-deployment/contracts/deployment-readiness.md`.
- [X] T023 [US3] Add failure-injection tests proving a broken migration, secret scan, build, readiness check, smoke check, or evaluation threshold blocks promotion in `apps/backend/tests/integration/deployment/test_release_gates.py`.
- [X] T024 [US3] Add explicit documentation that deterministic RAG evals are a release gate but live provider/LangSmith evals remain separate evidence in `docs/operations/evaluation-gates.md`.

## Phase 5: Observability, operations, and rollback (P2)

- [X] T025 [US4] Add environment/release/request fields to structured logs and LangSmith/OpenTelemetry traces with redaction tests in `apps/backend/src/atlas/observability/` and `apps/backend/tests/security/test_observability_redaction.py`.
- [X] T026 [US4] Add deployment dashboards/alerts for availability, readiness, errors, latency, tokens/cost, citation quality, queue/worker health, database, and provider failures in `infra/observability/`.
- [X] T027 [US4] Write deploy, incident, rollback, and migration compatibility runbooks in `docs/runbooks/deploy.md`, `docs/runbooks/incident-response.md`, and `docs/runbooks/rollback.md`.
- [X] T028 [US4] Add controlled rollback rehearsal and evidence retention in `scripts/verify-rollback.ps1` and `apps/backend/tests/integration/deployment/test_rollback.py`.
- [X] T029 [US4] Add beta domain, analytics, backup, alert, and runbook checklist linked to PRD item `SCL-011` in `docs/operations/beta-readiness.md`.

## Phase 6: Real environment activation (operator-assisted P1)

- [X] T030 [US1] Provision Vercel preview and production projects and record non-secret project identifiers in `docs/operations/environments.md`. (Evidence: project `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis`, main-branch deployment `dpl_Fn5qg6qNS9m88kWpu6Q2x6fP5481` and production deployment `dpl_8KpDGAy7wZSjeEyXEefnPWuH3JZi` are `READY`; `atlasai-lilac.vercel.app` serves HTTPS. Managed API activation remains T032-T036.)
- [ ] T031 [US2] Provision isolated Supabase preview/staging/production targets, enable required extensions/policies, and record redacted project metadata in `docs/operations/environments.md`.
- [ ] T032 [US2] Provision and verify the production Vercel API/Cron execution path for collection-scoped ingestion, configure HTTPS and `CRON_SECRET`, and record immutable deployment/Cron identifiers. The owner-approved architecture supersedes an always-on container for this beta; this task remains open until hosted evidence exists.
- [ ] T033 [US3] Configure environment-scoped secrets, CORS, auth callbacks, storage, model providers, and LangSmith project/tags without committing values.
- [ ] T034 [US3] Execute the complete quickstart against preview/staging and retain the release evidence bundle under `evals/results/`.
- [ ] T035 [US4] Verify traces, redaction, alerts, backups/restore, and rollback rehearsal in the real environment.
- [ ] T036 [US1] Execute production smoke tests in both locales and verify answer, comparison, report artifact, daily news, corpus freshness, auth/private-data, and truthful abstention behavior.
- [X] T044 [US2] Replace the placeholder `atlas-worker` entrypoint with deployable, fail-closed PostgreSQL/manifest/fetcher/embedding wiring, bounded queue polling, graceful shutdown, container command dispatch, and deterministic tests before T032. (Evidence: 22/22 focused tests, Ruff/mypy clean, image `sha256:443d1bba82c306df09c369b0a8cab6b66a5a9147d08fdee1bb67517fcce41e76`, container CLI dispatch verified, and missing-secret start rejected.)
- [X] T045 [US2] Wire the non-development FastAPI runtime to the verified cited-answer graph and durable operator ingestion service, report truthful model-provider readiness, and add deterministic production-composition/readiness tests before T032/T036. (Evidence: red contracts failed before implementation, focused runtime/readiness checks pass, the complete backend passes 436 tests/4 skips with Ruff and strict mypy clean, and image `sha256:bc1752b61a1b4e28ad3dacfea78aa6e01c096377cc96798a71f1fde578ca05a0` imports the runtime successfully.)

## Phase 7: Documentation and convergence

- [X] T037 [P] Update `README.md` with local versus deployed URLs, architecture, setup, environment boundaries, and evidence links.
- [X] T038 [P] Add/update the deployment ADR in `docs/adr/` explaining Vercel web/Cron, Supabase data/queue, the portable worker seam, migrations, and rollback decisions.
- [X] T039 [P] Update `docs/product/prd-v1.1-backlog.md`, `docs/product/feature-status-matrix.md`, and `docs/operations/` with Feature 018 traceability and SCL-011 status.
- [X] T040 Run Speckit analyze and resolve all critical inconsistencies across spec, plan, tasks, contracts, code, workflows, and docs. (The 2026-08-11 follow-up found and resolved worker execution as T044 and non-development API composition/readiness as T045; T031-T036 stay explicitly open.)
- [X] T041 Run Speckit converge after implementation; do not mark Feature 018 complete while operator-owned deployment evidence or required smoke tests are pending. (Follow-up convergence appended and completed T044-T045; the six external activation tasks remain open.)
- [X] T042 Run full local verification (`pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm test:e2e`, backend Ruff/mypy/pytest, security checks, deployment contract/smoke tests) and record results. (Evidence: backend 436 passed/4 skipped with repository Ruff and strict mypy clean after T045; frontend lint/typecheck, Vitest 35/35, Playwright 149 passed/4 hosted skips and production build pass; the final locale/flag delta passed 5/5 focused journeys; deployment/security follow-up passed 17 tests and the deployment secret scan. Hosted execution remains T034-T036, not this local gate.)
- [X] T043 Commit the feature in focused groups, update the README/ADR/evidence bundle, and link each commit/PR to this spec and task IDs. (Implementation commit: `e8de6b9`.)

## Phase 8: Interim portfolio beta activation (owner-approved)

- [X] T046 [US1] Deploy the existing FastAPI HTTP surface as an owner-approved Vercel Python Function for the cited-answer beta, configure Supabase/OpenAI/LangSmith secrets without committing values, set `NEXT_PUBLIC_API_ORIGIN`, and retain bilingual `/healthz`, `/readyz`, and cited-answer smoke evidence in `evals/results/vercel-api-beta-smoke-20260811.json`. This is an interim activation only; it does not close T032 or mark Feature 018 production-ready.

## Phase 9: Approved scheduled-ingestion architecture

- [X] T047 [US2] Record the owner-approved architecture decision in `spec.md`, `plan.md`, and `docs/adr/0015-production-deployment.md`: Vercel daily Cron, one collection per bounded invocation, Supabase as durable queue/database, and no additional always-on runtime. T032 remains open because hosted evidence is still required.
- [X] T048 [US2] Add the collection-scoped scheduled ingestion contract in `apps/backend/src/atlas/api/routes/operator_ingestion.py`, including `CRON_SECRET` bearer authentication, approved collection validation, redacted run summaries, and stable failure responses.
- [X] T049 [US2] Add deterministic UTC-date idempotency and collection filtering to the ingestion execution seam in `apps/backend/src/atlas/ingestion/scheduled.py`, `apps/backend/src/atlas/ingestion/service.py`, and `apps/backend/src/atlas/ingestion/worker.py`; preserve the existing last-good promotion and retry/dead-letter behavior.
- [X] T050 [US2] Configure production-only daily Cron routes and a five-minute bounded function limit in `apps/backend/vercel.json`, add `CRON_SECRET` placeholders to `.env.example` and `infra/env/`, and document the operational route in `docs/runbooks/corpus-refresh.md` and `docs/architecture/018-production-deployment.md`.
- [X] T051 [US2] Add contract and worker tests for missing/invalid Cron authentication, redacted summaries, UTC idempotency, collection isolation, and one-run bounded execution in `apps/backend/tests/contract/api/test_scheduled_ingestion.py` and `apps/backend/tests/integration/ingestion/test_worker.py`.
- [ ] T052 [US2] Deploy the scheduled route to Vercel production, configure the platform `CRON_SECRET`, invoke every approved collection once, and retain redacted run summaries and Vercel Cron logs under `evals/results/`; do not close T032-T036 without the remaining environment evidence.

## Requirement and success-criteria coverage

This matrix makes the owner-approved Cron change explicit for SpecKit review. A task may remain
open when its implementation is present but its hosted evidence is still missing.

| Requirement | Covered by tasks |
|---|---|
| FR-001 | T008, T030, T046, T052 |
| FR-002 | T008, T046 |
| FR-003 | T009, T010, T044, T045, T047-T052 |
| FR-004 | T013-T017, T031 |
| FR-005 | T003, T006, T013, T018, T031, T034 |
| FR-006 | T006, T013, T019, T031, T033, T036 |
| FR-007 | T008, T011, T012, T030, T031, T033 |
| FR-008 | T001-T006, T018, T020, T024, T042 |
| FR-009 | T003, T018, T022, T037, T042, T052 |
| FR-010 | T002, T045, T046, T052 |
| FR-011 | T025, T026, T035 |
| FR-012 | T027, T028, T035 |
| FR-013 | T005, T034, T036 |
| FR-014 | T002, T004, T006, T045, T046, T052 |
| FR-015 | T037, T040, T041, T052 |
| FR-016 | T047-T052 |
| SC-001 | T005, T030, T034, T036 |
| SC-002 | T003, T006, T013, T031, T034 |
| SC-003 | T003, T018, T037, T042, T052 |
| SC-004 | T004, T025, T033, T035, T042, T052 |
| SC-005 | T018, T020, T042 |
| SC-006 | T027, T028, T035 |
| SC-007 | T025, T026, T035 |
| SC-008 | T028, T035 |
| SC-009 | T026, T027, T035, T042 |
| SC-010 | T049, T051, T052 |

## Dependencies & Execution Order

- T001-T006 are the red contracts and block implementation.
- T007-T012 establish environment/runtime contracts and block release workflows.
- T013-T017 depend on T007 and block any real managed-data smoke test.
- T018-T024 depend on T001-T017 and block promotion.
- T025-T029 may proceed after runtime/release identifiers exist; T027 is required before T035.
- T044 is local runtime wiring required before T032; T030-T036 require operator credentials and external environments and cannot be faked by local tests.
- T037-T043 close only after implementation and real-environment evidence are reviewed.

## Definition of Done

Feature 018 is complete only when the repository gates pass, the public web/API are reachable in a
real environment, migrations and smoke contracts pass, release evidence is captured, secrets are
redacted, Supabase data/auth/storage boundaries are verified, observability and backup/restore are
demonstrated, rollback is rehearsed, and README/ADR/runbooks/status matrix are updated. Until then,
the feature remains open even if local Docker continues to work.
