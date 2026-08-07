# Tasks: CI/CD Hardening

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Database CI (Priority P1)

- [X] T001 [US1] Install backend dependencies and run Alembic migrations against the fresh CI PostgreSQL service in `.github/workflows/ci.yml`. Evidence: local `alembic upgrade head` reached `0015_expand_corpus_collections`.
- [X] T002 [US1] Run the versioned foundation, corpus-ingestion, retrieval, retention, provenance, collection-expansion, and daily-news SQL contracts with `ON_ERROR_STOP` in `.github/workflows/ci.yml`. Evidence: all 11 local SQL contracts passed.
- [X] T003 [US1] Add a CI smoke assertion that the migration head and required collection tables exist.

## Phase 2: Browser CI (Priority P2)

- [X] T004 [US2] Install the Playwright browser required by the existing web E2E suite in `.github/workflows/ci.yml`.
- [X] T005 [US2] Start the web test server and execute `pnpm --filter @atlas/web test:e2e` in CI. Evidence: local Node 24 run passed 12/12 journeys.
- [X] T006 [US2] Upload Playwright reports on failure without masking the failing job.

## Phase 3: Evaluation Evidence (Priority P3)

- [X] T007 [US3] Add an explicit evaluation-mode assertion or artifact check for deterministic fixture execution. Evidence: `atlas-eval` artifact records `execution_mode`.
- [X] T008 [US3] Document that live RAG and LangSmith evaluations remain separate non-PR gates. Evidence: CI invokes the deterministic dataset without `--results` or provider secrets.

## Phase 4: Verification

- [ ] T009 Run backend Ruff, mypy, and pytest locally; current exact CI command fails with 106 mypy diagnostics and remains open.
- [X] T010 Run the deterministic evaluator locally and inspect thresholds and execution mode.
- [X] T011 Validate workflow YAML and review the final diff for secrets or deployment side effects.
- [X] T012 Update implementation status and record commit evidence.

## Dependencies

- T001 blocks T002 and T003.
- T004 blocks T005 and T006.
- T001–T008 precede T009–T012.
