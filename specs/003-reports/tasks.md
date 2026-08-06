---

description: "Dependency-ordered implementation tasks for Feature 003"

---

# Tasks: Evidence-backed Research Reports

**Input**: Design documents from `/specs/003-reports/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/report-api.yaml`, `quickstart.md`

**Tests**: Required by the feature specification and project constitution. Write the tests first and verify they fail before implementation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish report package structure and deterministic fixtures without changing existing answer behavior.

- [X] T001 Create report package directories and module boundaries under `apps/backend/src/atlas/reports/` and `apps/backend/tests/{contract,unit,integration}/reports/`
- [X] T002 [P] Add report test fixtures and a deterministic completed-comparison source run in `apps/backend/tests/fixtures/reports/comparison_run.json`
- [X] T003 [P] Add report evaluation cases and expected citation manifests in `evals/datasets/report-v1.jsonl`
- [X] T004 [P] Add report feature types and API client boundary under `apps/web/src/features/reports/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared persistence, lifecycle, storage, and contract primitives required by all report stories.

- [X] T005 [P] Add report metadata tables, ownership digest, idempotency key, lifecycle state, artifact metadata, and expiry indexes in `database/migrations/versions/0016_reports.py`
- [X] T006 [P] Add SQL contract tests for report tables, lifecycle enum, ownership isolation, and idempotency uniqueness in `database/tests/008_reports.sql`
- [X] T007 [P] Define typed report entities and validation schemas in `apps/backend/src/atlas/reports/schemas.py`
- [X] T008 [P] Implement bounded local artifact storage with path-safe keys and content hashes in `apps/backend/src/atlas/reports/storage.py`
- [X] T009 Implement report repository and lifecycle service for quota, ownership, idempotency, expiry, and safe deletion in `apps/backend/src/atlas/reports/service.py`
- [X] T010 [P] Add shared report error codes, request IDs, and observability fields in `apps/backend/src/atlas/reports/observability.py`

**Checkpoint**: Foundational report persistence and storage contracts are testable before any renderer or route is added.

---

## Phase 3: User Story 1 - Generate a cited report (Priority: P1) MVP

**Goal**: Turn one completed technology-comparison run into a structured, citation-complete report job with progress and a terminal result.

**Independent Test**: Submit a valid request for the fixture comparison run, observe accepted/planning/rendering/completed progress, and verify every factual section cites source-run evidence.

### Tests for User Story 1 (write first)

- [X] T011 [P] [US1] Add OpenAPI contract tests for create/status/report progress endpoints in `apps/backend/tests/contract/reports/test_report_create_contract.py`
- [X] T012 [P] [US1] Add unit tests for valid/invalid `ReportSpec`, unsupported type, missing source run, and source ownership in `apps/backend/tests/unit/reports/test_schemas.py`
- [X] T013 [P] [US1] Add unit tests for idempotency replay and parameter conflict behavior in `apps/backend/tests/unit/reports/test_idempotency.py`
- [X] T014 [P] [US1] Add planner tests proving source citations are preserved and citation-less factual sections fail closed in `apps/backend/tests/unit/reports/test_planner.py`
- [X] T015 [P] [US1] Add API integration test for create-to-completed report lifecycle and downloads in `apps/backend/tests/contract/api/test_reports.py`

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement structured report section and citation manifest planning from completed comparison runs in `apps/backend/src/atlas/reports/planner.py`
- [X] T017 [US1] Implement report job orchestration and terminal state transitions in `apps/backend/src/atlas/reports/service.py`
- [X] T018 [US1] Add citation completeness, source-run membership, and fail-closed validation in `apps/backend/src/atlas/reports/validation.py`
- [X] T019 [US1] Add create/status/SSE progress routes matching `contracts/report-api.yaml` in `apps/backend/src/atlas/api/routes/reports.py`
- [X] T020 [US1] Register report routes and report-specific quota dependency in `apps/backend/src/atlas/api/main.py`
- [X] T021 [US1] Add report request/progress form and error states for the comparison MVP in `apps/web/src/features/reports/ReportRequest.tsx`
- [X] T022 [US1] Add report API client and progress event handling in `apps/web/src/features/reports/report-client.ts`
- [X] T023 [US1] Add browser journey for generating a cited report in `apps/web/tests/e2e/reports.spec.ts`

**Checkpoint**: User Story 1 works independently and produces a structured, citation-validated report job from a completed comparison run.

---

## Phase 4: User Story 2 - Download and manage artifacts (Priority: P2)

**Goal**: Render and validate DOCX/PDF artifacts, expose downloads, and make deletion/expiry safe and repeatable.

**Independent Test**: Generate a completed report, download both formats, parse and inspect them, delete twice, and confirm downloads return safe not-found semantics.

### Tests for User Story 2 (write first)

- [X] T024 [P] [US2] Add DOCX structural integrity, required references, and non-empty tests in `apps/backend/tests/unit/reports/test_renderers.py`
- [X] T025 [P] [US2] Add PDF parseability, required references, and non-empty tests in `apps/backend/tests/unit/reports/test_renderers.py`
- [X] T026 [P] [US2] Add artifact visual QA fixture/render test covering clipping and overflow failure in `apps/backend/tests/integration/reports/test_artifact_visual_qa.py`
- [X] T027 [P] [US2] Add download/delete/expired/foreign-owner contract tests in `apps/backend/tests/integration/reports/test_report_lifecycle.py`
- [X] T028 [P] [US2] Add integration test for repeat-safe download and deletion in `apps/backend/tests/integration/reports/test_report_lifecycle.py`

### Implementation for User Story 2

- [X] T029 [P] [US2] Implement DOCX renderer with headings, tables, citations, original-evidence labels, and metadata in `apps/backend/src/atlas/reports/renderers/docx.py`
- [X] T030 [P] [US2] Implement PDF renderer with the same intermediate representation and references in `apps/backend/src/atlas/reports/renderers/pdf.py`
- [X] T031 [US2] Implement structural and visual artifact validation before completed state in `apps/backend/src/atlas/reports/validation.py`
- [X] T032 [US2] Add download and repeat-safe delete/expiry routes in `apps/backend/src/atlas/api/routes/reports.py`
- [X] T033 [US2] Add download/delete controls and safe not-found messaging in `apps/web/src/features/reports/ReportRequest.tsx`
- [X] T034 [US2] Add browser journey for DOCX/PDF download and deletion in `apps/web/tests/e2e/reports-artifacts.spec.ts`

**Checkpoint**: User Stories 1 and 2 both work; artifacts are inspectable, downloadable, and safely retired.

---

## Phase 5: User Story 3 - Bilingual citation parity (Priority: P3)

**Goal**: Generate equivalent English and Mexican-Spanish presentation text while preserving citation IDs, URLs, and original evidence excerpts.

**Independent Test**: Generate equivalent reports from one source run in `en-US` and `es-MX`; compare citation manifests and inspect original-evidence labels.

### Tests for User Story 3 (write first)

- [X] T035 [P] [US3] Add unit tests for locale validation and deterministic heading/label translations in `apps/backend/tests/unit/reports/test_localization.py`
- [X] T036 [P] [US3] Add bilingual citation-manifest parity tests in `apps/backend/tests/unit/reports/test_localization.py`
- [X] T037 [P] [US3] Add browser journey for Spanish report generation and original-evidence labels in `apps/web/tests/e2e/reports-es.spec.ts`

### Implementation for User Story 3

- [X] T038 [P] [US3] Add report localization catalog for English and Mexican Spanish in `apps/backend/src/atlas/reports/planner.py`
- [X] T039 [US3] Apply localized presentation text without translating source excerpts or citation identities in `apps/backend/src/atlas/reports/planner.py`
- [X] T040 [US3] Add locale-aware labels and original-evidence messaging in `apps/web/src/features/reports/ReportRequest.tsx`
- [X] T041 [US3] Add bilingual deterministic report evaluation cases and citation parity assertions in `evals/datasets/report-v1.jsonl` and `apps/backend/tests/unit/evaluation/test_report_evals.py`

**Checkpoint**: All three stories are independently testable and preserve one evidence graph across locales.

---

## Phase 6: Polish, Verification, and Documentation Closure

**Purpose**: Verify the full vertical slice and update documentation from actual delivered artifacts.

- [X] T042 [P] Add report architecture decision record based on the delivered boundary in `docs/adr/0002-evidence-backed-report-boundary.md`
- [X] T043 [P] Add report architecture diagram and lifecycle/observability notes in `docs/architecture/003-reports.md`
- [X] T044 [P] Update README usage, report API quickstart, supported formats, locale behavior, and verification commands in `README.md`
- [ ] T045 Run `specs/003-reports/quickstart.md`, backend/web tests, SQL contracts, deterministic report evals, and artifact visual QA; record evidence in `docs/product/implementation-status.md`
- [ ] T046 Review final `spec.md`, `plan.md`, `tasks.md`, actual diff, and commit history; update README, relevant ADRs, and architecture docs only for behavior actually delivered, then run link and SpecKit consistency checks

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) precedes Foundational (Phase 2).
- Foundational (Phase 2) blocks all user-story work.
- User stories proceed in priority order for the MVP: US1, then US2, then US3; US2 depends on the structured report representation from US1 and US3 depends on the same representation.
- Polish and the mandatory documentation closure task run only after the selected stories and verification pass.

### Parallel Opportunities

- T002-T004 can run in parallel.
- T005-T008 and T010 can run in parallel before T009.
- US1 tests T011-T015 can run in parallel; planner, schemas, and frontend work can proceed on separate files after foundational contracts exist.
- US2 renderer tests and contract tests T024-T028 can run in parallel; DOCX and PDF renderers T029-T030 can run in parallel.
- US3 tests T035-T037 and localization catalog T038 can run in parallel after the P1 representation exists.
- T042-T044 can run in parallel, but T046 is last and must use the final diff and commits.

## Implementation Strategy

1. Complete Phase 1 and Phase 2, then stop to verify migration and contract primitives.
2. Deliver US1 as the portfolio MVP: completed comparison run -> cited report job -> progress -> validated structured report.
3. Add US2 so the report is a real inspectable DOCX/PDF artifact with safe lifecycle controls.
4. Add US3 for Spanish presentation and citation parity.
5. Run the full verification matrix and complete T046 as the final task before declaring Feature 003 closed.

## Requirements and Success-Criteria Traceability

| Requirement | Primary tasks | Verification |
|---|---|---|
| FR-001 | T012, T018, T019 | T015, T027 |
| FR-002 | T012, T016 | T041 |
| FR-003 | T007, T012, T019 | T011 |
| FR-004 | T005, T009, T017 | T015, T028 |
| FR-005 | T009, T013 | T015, T028 |
| FR-006 | T016, T029, T030 | T014, T024, T025 |
| FR-007 | T016, T018, T029, T030 | T014, T024, T025, T036 |
| FR-008 | T029, T030, T031, T032 | T024-T028 |
| FR-009 | T026, T031 | T026 |
| FR-010 | T038-T040 | T035-T037, T041 |
| FR-011 | T009, T020 | T013, T015 |
| FR-012 | T009, T032, T033 | T027, T028, T034 |
| FR-013 | T008, T010, T018 | T026, T027, T045 |
| FR-014 | T005, T009, T010, T031 | T024-T028, T045 |
| FR-015 | T042-T046 | T046 |
| SC-001 | T017, T045 | T015, T045 |
| SC-002 | T018, T045 | T014, T015 |
| SC-003 | T024-T031, T045 | T024-T026, T045 |
| SC-004 | T035-T041 | T036, T041 |
| SC-005 | T009, T013, T032 | T013, T028 |
| SC-006 | T009, T031-T033 | T027, T028, T034 |

## Notes

- `[P]` means the task can run in parallel without editing the same file or depending on incomplete work.
- Every task includes an exact file path and maps to a story or shared phase.
- Tests must be written and observed failing before the corresponding implementation task.
- The final documentation task is mandatory and must not invent behavior absent from the final spec, plan, tasks, diff, or commits.
