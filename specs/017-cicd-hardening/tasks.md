# Tasks: CI/CD Hardening

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Database CI (Priority P1)

- [X] T001 [US1] Install backend dependencies and run Alembic migrations against the fresh CI PostgreSQL service in `.github/workflows/ci.yml`. Evidence: on 2026-08-11 an isolated empty database reached hosted-equivalent head `agent_tool_rls` through the complete migration chain.
- [X] T002 [US1] Run all versioned SQL contracts with `ON_ERROR_STOP` in `.github/workflows/ci.yml`. Evidence: all 19 SQL contract files passed against the isolated database on 2026-08-11.
- [X] T003 [US1] Add a CI smoke assertion that the migration head and required collection tables exist.

## Phase 2: Browser CI (Priority P2)

- [X] T004 [US2] Install the Playwright browser required by the existing web E2E suite in `.github/workflows/ci.yml`.
- [X] T005 [US2] Start the web test server and execute `pnpm --filter @atlas/web test:e2e` in CI. Evidence: local Node 24 run passed 12/12 journeys.
- [X] T006 [US2] Upload Playwright reports on failure without masking the failing job.

## Phase 3: Evaluation Evidence (Priority P3)

- [X] T007 [US3] Add an explicit evaluation-mode assertion or artifact check for deterministic fixture execution. Evidence: `atlas-eval` artifact records `execution_mode`.
- [X] T008 [US3] Document that live RAG and LangSmith evaluations remain separate non-PR gates. Evidence: CI invokes the deterministic dataset without `--results` or provider secrets.

## Phase 4: Verification

- [X] T009 Run backend Ruff, mypy, and pytest locally; exact CI command `mypy src tests` passes with 314 files, Ruff passes, and pytest reports 304 passed / 4 skipped.
- [X] T010 Run the deterministic evaluator locally and inspect thresholds and execution mode.
- [X] T011 Validate workflow YAML and review the final diff for secrets or deployment side effects.
- [X] T012 Update implementation status and record commit evidence.

## Dependencies

- T001 blocks T002 and T003.
- T004 blocks T005 and T006.
- T001–T008 precede T009–T012.

## Phase 5: Convergence

- [X] T013 Complete strict mypy cleanup for production and tests without blanket module exclusions; exact command `mypy src tests` exits successfully (FR-007, SC-003).

## Phase 6: Hosted CI regression repair

- [X] T014 [US1] Make migration `0026_supabase_extension_security` self-contained on both Supabase and a fresh local/CI pgvector database by creating the `extensions` schema idempotently before moving pgvector.
- [X] T015 [US1] Correct root-relative monorepo paths and backend `PYTHONPATH` in `.github/workflows/ci.yml`; focused security and deployment-contract suites pass locally before hosted verification.
- [X] T016 Update the feature verification document with the fresh-database reproduction, root cause, correction, and regression evidence.
