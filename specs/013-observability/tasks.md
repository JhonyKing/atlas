# Tasks: LangSmith Quality Observability

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Foundation

- [X] T001 [P] Add typed settings for optional LangSmith endpoint, project, workspace and tracing flag in `apps/backend/src/atlas/config.py`.
- [X] T002 [P] Add the internal tracing port and no-op implementation in `apps/backend/src/atlas/observability/langsmith.py`.
- [X] T003 Write redaction tests for question, answer, excerpt, authorization, secret and cookie fields in `apps/backend/tests/unit/observability/test_observability.py` and `test_langsmith.py`.
- [X] T004 Document secret-only configuration and current LangSmith environment variables in `.env.example` and `docs/operations/langsmith-runbook.md`.

## Phase 2: Answer lifecycle (P1)

- [X] T005 [P] Instrument request/run creation and terminal status in `apps/backend/src/atlas/api/answer_service.py`.
- [X] T006 [P] Instrument retrieval, model generation, verification and answer terminal status in `apps/backend/src/atlas/observability/`.
- [X] T007 Add locale, model, prompt, retrieval, embedding, application and corpus snapshot version tags without content in `apps/backend/src/atlas/observability/langsmith.py`.
- [X] T008 Add unit and contract tests proving LangSmith absence/unavailability does not fail answer requests.

## Phase 3: Feedback and evals (P1)

- [ ] T009 Link feedback categories, especially incorrect citation, to a review-case interface without copying PII.
- [X] T010 Add versioned dataset metadata and online evaluation linkage in `evals/datasets/` and `evals/run_langsmith.py`.
- [X] T011 Add opt-in network smoke test guarded by `ATLAS_LANGSMITH_SMOKE=1` and never print credentials.
- [X] T012 Add CI-safe offline evaluation export with dataset, experiment, commit and corpus identifiers.

## Phase 4: Operations (P2)

- [ ] T013 Add dashboard query definitions for latency, TTFT, errors, cost, citation, abstention and feedback by locale/snapshot.
- [ ] T014 Add retention/deletion and key-rotation runbook with a trace redaction checklist.
- [ ] T015 Run analyze/converge, record evidence, and update the PRD traceability matrix.

## Requirement coverage

| Requirement | Tasks |
|---|---|
| FR-OBS-001 | T005, T006 |
| FR-OBS-002 | T006, T007, T013 |
| FR-OBS-003 | T003, T008, T011, T014 |
| FR-OBS-004 | T001, T002, T008, T011 |
| FR-OBS-005 | T009, T010, T012 |
| FR-OBS-006 | T014 |
| FR-OBS-007 | T013, T014 |
| SC-OBS-001 | T005, T008 |
| SC-OBS-002 | T010, T013 |
| SC-OBS-003 | T008, T011 |
| SC-OBS-004 | T003 |
| SC-OBS-005 | T010, T012 |
