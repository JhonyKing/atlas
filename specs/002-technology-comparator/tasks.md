# Tasks: Evidence-Backed Technology Comparator

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md), [contracts/](contracts/)

**Execution rule**: Write a failing test or evaluation case before each behavior change, then
implement the smallest change that makes it pass.

## Phase 1: Setup

- [X] T001 [P] Add comparison package entry points and typed configuration defaults in `apps/backend/src/atlas/comparison/__init__.py` and `apps/backend/src/atlas/config.py` for the five-comparison rolling window and supported criterion IDs. (Evidence: comparison exports and `atlas_anonymous_comparison_limit=5`; config/schema tests pass.)
- [X] T002 [P] Add the comparison OpenAPI and SSE contracts to the generated contract registry in `apps/backend/src/atlas/api/contracts.py` and verify links from `specs/002-technology-comparator/contracts/`. (Evidence: registry test confirms both Spec Kit contract files, three routes and seven event names.)
- [X] T003 [P] Add the comparison feature route and page placeholders to `apps/web/src/app/[locale]/compare/page.tsx` and `apps/web/src/features/comparison/` without exposing an unverified result. (Evidence: bilingual `/en/compare` and `/es/compare` placeholder; frontend lint and typecheck pass.)

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

- [X] T012 [P] [US1] Write failing API/SSE contract tests for `POST /v1/comparisons`, `GET /v1/comparisons/{run_id}`, and repeat-safe `DELETE /v1/comparisons/{run_id}` in `apps/backend/tests/contract/api/test_comparisons.py`. (Evidence: five contract tests cover streaming headers, status, cancellation, missing idempotency and invalid selection.)
- [X] T013 [P] [US1] Write failing event-order tests for accepted, retrieval, normalization, verification, completed, cancellation and failure events in `apps/backend/tests/unit/comparison/test_events.py`. (Evidence: monotonic IDs, terminal enforcement, progress redaction and supported-cell evidence gate.)
- [X] T014 [P] [US1] Write failing persistence tests for matrix cells, evidence links, snapshot identity and terminal status in `apps/backend/tests/integration/comparison/test_repository.py`. (Evidence: two integration tests verify visitor isolation, immutable snapshot identity, cell evidence IDs and terminal completion requirements.)
- [X] T015 [US1] Implement comparison-run persistence and repository methods in `apps/backend/src/atlas/persistence/comparison_repository.py` to satisfy T014. (Evidence: in-memory and PostgreSQL repositories persist runs, matrices, cells, evidence links, snapshots and terminal status; repository tests pass.)
- [X] T016 [US1] Write failing normalization tests for units, periods, versions, missing values and incompatible definitions in `apps/backend/tests/unit/comparison/test_normalization.py`. (Evidence: four tests cover preserved context, missing values, incompatible units and conflicting values.)
- [X] T017 [US1] Implement deterministic criterion extraction and normalization in `apps/backend/src/atlas/comparison/normalization.py` to satisfy T016. (Evidence: explicit supported/unsupported/partial/contradictory cells, no inferred unit conversion, plus migration `0014_comparison_cell_context`; targeted tests pass.)
- [X] T018 [US1] Write failing workflow tests for two-technology fan-out, evidence assembly, cancellation and terminal verification in `apps/backend/tests/unit/comparison/test_workflow.py`. (Evidence: two async tests cover two-technology matrix assembly, evidence IDs and cancellation before publication.)
- [X] T019 [US1] Implement the explicit comparison workflow and evidence gate in `apps/backend/src/atlas/comparison/workflow.py` to satisfy T018. (Evidence: retrieve → extract → normalize → evidence-gate flow with cancellation checks; workflow tests pass.)
- [X] T020 [US1] Implement authenticated-by-anonymous-identity comparison API routes and SSE streaming in `apps/backend/src/atlas/api/routes/comparisons.py` to satisfy T012 and T013. (Evidence: route uses anonymous HMAC identity, idempotency header, quota conflict handling, GET/DELETE ownership checks and SSE response headers; contract tests pass.)
- [X] T021 [US1] Implement the typed comparison API client and cancellation handling in `apps/web/src/features/comparison/api.ts`. (Evidence: typed request/run/matrix/event contracts, SSE parser, run ID capture, GET status and DELETE cancellation; frontend lint/typecheck pass.)
- [X] T022 [US1] Implement the accessible two-technology comparison form, progress state, matrix, cell evidence and unsupported-state UI in `apps/web/src/features/comparison/ComparisonPage.tsx` and `apps/web/src/features/comparison/ComparisonMatrix.tsx`. (Evidence: keyboard-accessible fieldsets, progress/cancel controls, terminal-only matrix rendering and explicit cell states; frontend lint/typecheck pass.)
- [X] T023 [US1] Add the supported two-technology Playwright journey and evidence inspection assertions in `apps/web/tests/e2e/comparison-supported.spec.ts`. (Evidence: Playwright Chromium journey passes; terminal event renders supported and unsupported cells with evidence counts/explanations.)

## Phase 4: User Story 2 - Explain Missing and Conflicting Evidence (Priority: P1)

**Goal**: Unsupported, partial and contradictory cells are explicit and safe.

**Independent Test**: Prepared missing and contradiction cases render the correct cell state without
invented values or unauthorized actions.

- [X] T024 [P] [US2] Write failing cell-state and contradiction tests in `apps/backend/tests/unit/comparison/test_cell_verification.py`. (Evidence: tests cover all four states and reject populated cells without evidence or explanations.)
- [X] T025 [US2] Implement supported, unsupported, partial and contradictory cell verification in `apps/backend/src/atlas/comparison/verification.py` to satisfy T024. (Evidence: final matrix evidence gate enforces explicit state rules; tests pass.)
- [X] T026 [P] [US2] Add malicious-source and unauthorized-instruction fixtures for comparison evidence in `apps/backend/tests/fixtures/security/comparison_malicious_source.md` and `apps/backend/tests/integration/security/test_comparison_prompt_injection.py`. (Evidence: malicious instruction fixture is treated as data and parsed without execution.)
- [X] T027 [US2] Enforce the evidence-only prompt boundary and no-action-tools policy in `apps/backend/src/atlas/providers/prompts/comparison.py` to satisfy T026. (Evidence: prompt explicitly marks source as untrusted, exposes no tools, and security test passes.)
- [X] T028 [P] [US2] Add temporal, version and stale-source regression cases to `evals/datasets/comparison-v1.jsonl` and `apps/backend/tests/unit/comparison/test_constraints.py`. (Evidence: four deterministic cases cover missing price, incompatible units, stale dates and version mismatch; constraint tests pass.)
- [X] T029 [US2] Add unsupported, partial, contradiction and constraint explanations to `apps/web/src/features/comparison/ComparisonMatrix.tsx` and add the Playwright journey in `apps/web/tests/e2e/comparison-evidence-states.spec.ts`. (Evidence: UI renders explicit states/explanations; Chromium journey passes.)

## Phase 5: User Story 3 - Bilingual and Four-Technology Comparison (Priority: P2)

**Goal**: The same comparison remains semantically identical in English and Spanish and supports
four rows.

**Independent Test**: The same request in `/en/compare` and `/es/compare` preserves all IDs, values,
dates, versions and cell states.

- [X] T030 [P] [US3] Write failing locale catalog, route and semantic-parity tests in `apps/web/src/features/comparison/__tests__/comparison-locale.test.tsx` and `apps/web/tests/e2e/comparison-locale-parity.spec.ts`. (Evidence: component parity test is present; Chromium parity test preserves technology IDs and values across `/en/compare` and `/es/compare`; Vitest execution remains blocked by the existing Windows resolver issue.)
- [X] T031 [US3] Add comparison message catalogs, `/en/compare` and `/es/compare` route handling, original-language evidence labels and locale propagation in `apps/web/src/i18n/` and `apps/web/src/features/comparison/`. (Evidence: catalog entries exist in both locales; request language and labels follow locale; parity journey passes.)
- [X] T032 [P] [US3] Add deterministic two-, three- and four-technology comparison cases with expected cell states and evidence IDs in `evals/datasets/comparison-v1.jsonl`. (Evidence: 20 requests, 17 matrix cases and a four-row Anthropic fixture are present and tested against the promoted snapshot.)
- [X] T033 [US3] Add four-technology validation, keyboard navigation and locale-parity Playwright coverage in `apps/web/tests/e2e/comparison-four-tech.spec.ts`. (Evidence: Chromium journey passes in English and Spanish with four selected technologies and 4 matrix rows.)

## Phase 6: Polish and Cross-Cutting Quality Gates

- [X] T034 [P] Add comparison request, retrieval, normalization, verification, locale, model and snapshot metadata to the LangSmith trace tree in `apps/backend/src/atlas/comparison/observability.py` and cover it in `apps/backend/tests/unit/comparison/test_observability.py`. (Evidence: root/stage trace tree carries safe counts, locale, model, snapshot, quota and branch labels without content; test passes.)
- [X] T035 Add deterministic comparison evaluation and matrix/citation parity reporting in `apps/backend/src/atlas/evaluation/comparison_cli.py` and `evals/evaluators/comparison.py`. (Evidence: CLI reports structure accuracy, state accuracy and evidence-ID parity; deterministic fixture run passes 2 matrix cases.)
- [X] T036 Run the feature quickstart and all backend/frontend quality gates, recording results in `evals/results/002-technology-comparator-baseline.md`. (Evidence: 177 backend tests passed, migrations upgraded, comparison evaluator 17 matrix cases, frontend lint/typecheck passed and 12 Playwright tests passed.)
- [X] T037 Run Spec Kit analyze/converge, resolve critical findings, update the PRD traceability matrix, and mark only evidenced tasks complete in `docs/product/prd-v1.1-traceability.md`. (Evidence: prerequisite check passed; analysis found runtime wiring, fourth corpus, 20-case metrics and Vitest runner gaps; convergence tasks T038–T041 were appended and PRD/backlog traceability updated.)

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

## Phase 7: Convergence

- [X] T038 [US1] Wire a production-safe comparison run service into `create_runtime_app()` with the separate quota, verified snapshot selection, retrieval/workflow, persistence, trace tree and terminal SSE events per FR-CMP-001–FR-CMP-010. (Evidence: live Spanish four-technology run completed against snapshot `660b0578-992f-43d2-9722-fa0c49568bbd`; terminal SSE and trace metadata are recorded.)
- [X] T039 [US3] Approve, ingest and verify a fourth supported technology collection, then add the four-technology dataset and Playwright journey for FR-CMP-001, FR-CMP-011 and SC-CMP-006. (Evidence: Anthropic review approved, four sources and 677 chunks are present in the promoted snapshot, and the bilingual four-row journey passes.)
- [X] T040 [US1] Expand `evals/datasets/comparison-v1.jsonl` to at least 20 representative comparison requests and record matrix citation precision, useful-progress latency and terminal latency for SC-CMP-001, SC-CMP-002 and SC-CMP-004. (Evidence: dataset has 20 requests and 17 deterministic matrix cases with structure/state/evidence parity 1.0; the owner reviewed corrected run `ed9e093f-74ed-4d47-a5c6-8a05ace0e505` and accepted 11/11 cited cells for precision 1.0, with `openai/context` correctly unsupported; optimized live run `2a317ed1-a0b9-4f6c-9227-f6fcdf93f382` records useful progress at 0 ms and terminal latency at 18,590 ms. The superseded run remains preserved as regression evidence.)
- [X] T041 [US3] Execute the locale component test with a working Vitest Windows resolver and record the result in `evals/results/002-technology-comparator-baseline.md`. (Evidence: bundled Node 24/Vitest 4.1.10 run passed 8 files and 20 tests; the sandboxed Node 20 invocation remains an environment permission issue, not a test failure.)

## Convergence evidence update (2026-08-06)

- T038 is evidenced by a live four-technology Spanish comparison against snapshot
  `660b0578-992f-43d2-9722-fa0c49568bbd`.
- T039 is evidenced by verified Anthropic and Gemini collections, the 20-request dataset and the
  bilingual four-row journey.
- T040 is closed with owner-reviewed citation precision 1.0 (11/11 cited cells) from corrected run
  `ed9e093f-74ed-4d47-a5c6-8a05ace0e505` and live latency evidence from optimized run
  `2a317ed1-a0b9-4f6c-9227-f6fcdf93f382` (0 ms useful progress, 18,590 ms terminal).

## Phase 8: Convergence

- [X] T042 [US1] Reduce comparison terminal latency per SC-CMP-004 and the plan performance goal:
  execute independent technology/criterion extraction branches concurrently with bounded
  concurrency, preserve cancellation and LangSmith stage metadata, emit a measurable useful-progress
  timestamp, and add a deterministic/integration regression proving the workflow remains safe and
  reaches the terminal budget under the launch scenario (Evidence: 37 comparison tests pass; Ruff and
  targeted mypy pass; the live Spanish four-technology run completed 12 cells with useful progress at
  0 ms and terminal latency 18,590 ms in `evals/results/live-comparator-t042-20260807.json`).

## Phase 9: Convergence

- [X] T043 [US2] Preserve complementary qualitative observations instead of labeling them as
  conflicting values: add an explicit observation relationship (`supports`, `complements`, or
  `contradicts`) to structured extraction, keep a bounded combined value for complementary claims,
  retain explicit contradiction handling, enforce that every `ComparisonCell.evidence_ids` belongs to
  the cell's retrieved branch, and add regression tests plus a machine-generated live review artifact
  that validates every cited ID against its source metadata (partial, HIGH). (Evidence: full backend
  suite 311 passed/4 skipped; comparison suite 42 passed; new run `ed9e093f-74ed-4d47-a5c6-8a05ace0e505`
  completed in 24,565 ms; `evals/results/live-comparator-t043-20260807-fixed-review.md` and its
  machine-readable JSON record report 40/40 evidence IDs resolved with zero collection mismatches.
  The corrected evidence mapping was subsequently owner-reviewed and accepted under T040.)
