# Tasks: Evidence-Backed Technology Comparator

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md), [contracts/](contracts/)

**Execution rule**: Write a failing test or evaluation case before each behavior change, then
implement the smallest change that makes it pass.

## Phase 1: Setup

- [X] T001 [P] Add comparison package entry points and typed configuration defaults in `apps/backend/src/atlas/comparison/__init__.py` and `apps/backend/src/atlas/config.py` for the five-comparison rolling window and supported criterion IDs. (Evidence: comparison exports and `atlas_anonymous_comparison_limit=5`; config/schema tests pass.)
- [ ] T002 [P] Add the comparison OpenAPI and SSE contracts to the generated contract registry in `apps/backend/src/atlas/api/contracts.py` and verify links from `specs/002-technology-comparator/contracts/`.
- [ ] T003 [P] Add the comparison feature route and page placeholders to `apps/web/src/app/[locale]/compare/page.tsx` and `apps/web/src/features/comparison/` without exposing an unverified result.

## Phase 2: Foundational

- [X] T004 [P] Write failing domain tests for `ComparisonRequest`, `ComparisonRun`, `ComparisonMatrix`, `ComparisonCell`, criterion IDs and cell-state rules in `apps/backend/tests/unit/comparison/test_schemas.py`. (Evidence: 14 domain/config tests cover selection, lifecycle, matrix coordinates, evidence requirements and criteria.)
- [X] T005 Implement typed comparison domain schemas and validation in `apps/backend/src/atlas/comparison/schemas.py` to satisfy T004. (Evidence: strict Pydantic contracts for requests, runs, matrices and cells; targeted tests pass.)
- [X] T006 [P] Write failing PostgreSQL contract tests for comparison runs, cells, evidence links, snapshot IDs, retention and idempotency in `database/tests/006_comparisons.sql`. (Evidence: SQL contract checks all five tables, unique visitor/key identity, snapshot/evidence foreign keys and retention index.)
- [X] T007 Implement versioned comparison tables, indexes, retention and evidence foreign keys in `database/migrations/versions/` to satisfy T006. (Evidence: migration `0012_comparisons`; Alembic upgrade and `psql -f database/tests/006_comparisons.sql` pass against local PostgreSQL.)
- [X] T008 [P] Write failing comparison-quota tests for five accepted runs, rolling expiry, idempotency and visitor isolation in `apps/backend/tests/integration/security/test_comparison_quota.py`. (Evidence: three integration tests cover five-run limit, sixth-run denial, rolling expiry, repeat safety and visitor isolation.)
- [X] T009 Implement the separate comparison quota reservation in `apps/backend/src/atlas/persistence/comparison_quota.py` and `database/functions/reserve_comparison_quota.sql` to satisfy T008. (Evidence: in-memory and PostgreSQL repositories plus migration `0013_comparison_quota`; local SQL smoke test accepted five and denied the sixth.)
- [X] T010 [P] Write failing retrieval fan-out tests for independent technology filters, selected snapshot and deterministic branch ordering in `apps/backend/tests/unit/comparison/test_retrieval.py`. (Evidence: two async tests verify four ordered branches, shared immutable snapshot, independent filters and no cross-technology evidence.)
- [X] T011 Implement the comparison retrieval port and fan-out service in `apps/backend/src/atlas/comparison/retrieval.py` to satisfy T010 using the existing corpus repository. (Evidence: deterministic `asyncio.gather` fan-out, per-branch constraints, stable de-duplication and corpus adapter; 11 targeted tests pass.)

## Phase 3: User Story 1 - Compare Selected Technologies (Priority: P1)

**Goal**: A visitor can compare two technologies and inspect a cited matrix.

**Independent Test**: A two-technology request returns a terminal matrix with explicit criteria and
evidence IDs for every populated cell.

- [ ] T012 [P] [US1] Write failing API/SSE contract tests for `POST /v1/comparisons`, `GET /v1/comparisons/{run_id}`, and repeat-safe `DELETE /v1/comparisons/{run_id}` in `apps/backend/tests/contract/api/test_comparisons.py`.
- [ ] T013 [P] [US1] Write failing event-order tests for accepted, retrieval, normalization, verification, completed, cancellation and failure events in `apps/backend/tests/unit/comparison/test_events.py`.
- [ ] T014 [P] [US1] Write failing persistence tests for matrix cells, evidence links, snapshot identity and terminal status in `apps/backend/tests/integration/comparison/test_repository.py`.
- [ ] T015 [US1] Implement comparison-run persistence and repository methods in `apps/backend/src/atlas/persistence/comparison_repository.py` to satisfy T014.
- [ ] T016 [US1] Write failing normalization tests for units, periods, versions, missing values and incompatible definitions in `apps/backend/tests/unit/comparison/test_normalization.py`.
- [ ] T017 [US1] Implement deterministic criterion extraction and normalization in `apps/backend/src/atlas/comparison/normalization.py` to satisfy T016.
- [ ] T018 [US1] Write failing workflow tests for two-technology fan-out, evidence assembly, cancellation and terminal verification in `apps/backend/tests/unit/comparison/test_workflow.py`.
- [ ] T019 [US1] Implement the explicit comparison workflow and evidence gate in `apps/backend/src/atlas/comparison/workflow.py` to satisfy T018.
- [ ] T020 [US1] Implement authenticated-by-anonymous-identity comparison API routes and SSE streaming in `apps/backend/src/atlas/api/routes/comparisons.py` to satisfy T012 and T013.
- [ ] T021 [US1] Implement the typed comparison API client and cancellation handling in `apps/web/src/features/comparison/api.ts`.
- [ ] T022 [US1] Implement the accessible two-technology comparison form, progress state, matrix, cell evidence and unsupported-state UI in `apps/web/src/features/comparison/ComparisonPage.tsx` and `apps/web/src/features/comparison/ComparisonMatrix.tsx`.
- [ ] T023 [US1] Add the supported two-technology Playwright journey and evidence inspection assertions in `apps/web/tests/e2e/comparison-supported.spec.ts`.

## Phase 4: User Story 2 - Explain Missing and Conflicting Evidence (Priority: P1)

**Goal**: Unsupported, partial and contradictory cells are explicit and safe.

**Independent Test**: Prepared missing and contradiction cases render the correct cell state without
invented values or unauthorized actions.

- [ ] T024 [P] [US2] Write failing cell-state and contradiction tests in `apps/backend/tests/unit/comparison/test_cell_verification.py`.
- [ ] T025 [US2] Implement supported, unsupported, partial and contradictory cell verification in `apps/backend/src/atlas/comparison/verification.py` to satisfy T024.
- [ ] T026 [P] [US2] Add malicious-source and unauthorized-instruction fixtures for comparison evidence in `apps/backend/tests/fixtures/security/comparison_malicious_source.md` and `apps/backend/tests/integration/security/test_comparison_prompt_injection.py`.
- [ ] T027 [US2] Enforce the evidence-only prompt boundary and no-action-tools policy in `apps/backend/src/atlas/providers/prompts/comparison.py` to satisfy T026.
- [ ] T028 [P] [US2] Add temporal, version and stale-source regression cases to `evals/datasets/comparison-v1.jsonl` and `apps/backend/tests/unit/comparison/test_constraints.py`.
- [ ] T029 [US2] Add unsupported, partial, contradiction and constraint explanations to `apps/web/src/features/comparison/ComparisonMatrix.tsx` and add the Playwright journey in `apps/web/tests/e2e/comparison-evidence-states.spec.ts`.

## Phase 5: User Story 3 - Bilingual and Four-Technology Comparison (Priority: P2)

**Goal**: The same comparison remains semantically identical in English and Spanish and supports
four rows.

**Independent Test**: The same request in `/en/compare` and `/es/compare` preserves all IDs, values,
dates, versions and cell states.

- [ ] T030 [P] [US3] Write failing locale catalog, route and semantic-parity tests in `apps/web/src/features/comparison/__tests__/comparison-locale.test.tsx` and `apps/web/tests/e2e/comparison-locale-parity.spec.ts`.
- [ ] T031 [US3] Add comparison message catalogs, `/en/compare` and `/es/compare` route handling, original-language evidence labels and locale propagation in `apps/web/src/i18n/` and `apps/web/src/features/comparison/`.
- [ ] T032 [P] [US3] Add deterministic two-, three- and four-technology comparison cases with expected cell states and evidence IDs in `evals/datasets/comparison-v1.jsonl`.
- [ ] T033 [US3] Add four-technology validation, keyboard navigation and locale-parity Playwright coverage in `apps/web/tests/e2e/comparison-four-tech.spec.ts`.

## Phase 6: Polish and Cross-Cutting Quality Gates

- [ ] T034 [P] Add comparison request, retrieval, normalization, verification, locale, model and snapshot metadata to the LangSmith trace tree in `apps/backend/src/atlas/comparison/observability.py` and cover it in `apps/backend/tests/unit/comparison/test_observability.py`.
- [ ] T035 Add deterministic comparison evaluation and matrix/citation parity reporting in `apps/backend/src/atlas/evaluation/comparison_cli.py` and `evals/evaluators/comparison.py`.
- [ ] T036 Run the feature quickstart and all backend/frontend quality gates, recording results in `evals/results/002-technology-comparator-baseline.md`.
- [ ] T037 Run Spec Kit analyze/converge, resolve critical findings, update the PRD traceability matrix, and mark only evidenced tasks complete in `docs/product/prd-v1.1-traceability.md`.

## Dependencies and Execution Order

- Phase 1 → Phase 2 → US1 → US2 → US3 → Phase 6.
- US2 depends on the US1 matrix and evidence contracts.
- US3 depends on stable locale-independent matrix output from US1 and US2.
- T004, T006, T008 and T010 can be authored in parallel; their implementations are foundational.
- T012–T014 and T016 can be authored in parallel after Phase 2.
- T024, T026 and T028 can be authored in parallel after US1.

## MVP Scope

The first independently demonstrable increment is US1 with two technologies, three criteria,
evidence-linked cells, progress and cancellation. US2 is required before calling the comparator
trustworthy. US3 is required before calling the public bilingual feature complete.

## Requirement Coverage

| Requirement group | Tasks |
|---|---|
| FR-CMP-001–FR-CMP-004 (selection, criteria and matrix shape) | T004–T005, T012–T023 |
| FR-CMP-005–FR-CMP-008 (cell evidence, states, constraints and normalization) | T006–T011, T014–T019, T024–T029 |
| FR-CMP-009–FR-CMP-010 (progress, cancellation, idempotency and validation) | T008–T009, T012–T013, T020–T023 |
| FR-CMP-011 (bilingual parity) | T030–T033 |
| FR-CMP-012 (untrusted source boundary) | T026–T027, T029 |
| FR-CMP-013 (comparison-specific matrix experience) | T012–T023, T029, T033 |
| SC-CMP-001–SC-CMP-004 (matrix quality, citation, safety and performance) | T012–T029, T035–T036 |
| SC-CMP-005–SC-CMP-006 (locale and semantic parity) | T030–T033, T035 |
| SC-CMP-007 (source-injection safety) | T026–T027, T035 |
| SC-CMP-008 (external usability) | T033, T036 |
