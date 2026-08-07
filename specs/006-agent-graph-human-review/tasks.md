# Tasks: Agent Graph, Planning, Checkpoints, and Human Review

**Input**: Design documents from `specs/006-agent-graph-human-review/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`
**Tests**: Required first for routing, persistence, security, and publication boundaries.

## Phase 1: Setup and contracts

- [ ] T001 Create agent unit, contract, integration, security, and browser test directories.
- [ ] T002 Add deterministic fixtures for questions, route plans, checkpoints, reviews, and clock control.
- [ ] T003 Add Feature 006 verification script/package command and bounded settings for node/checkpoint/review TTLs.
- [ ] T004 Add failing `AtlasState`, `RoutePlan`, `Checkpoint`, `ReviewRequest`, and `NodeEvent` schema tests.
- [ ] T005 Add failing graph route/node-order contract tests for factual, comparison, report, abstention, and cancellation paths.
- [ ] T006 Add failing checkpoint/replay tests for crash recovery, duplicate resume, corruption, expiry, and concurrency.
- [ ] T007 Add failing review contract/security tests for approve, validated edit, reject, unauthorized, expiry, duplicate decision, and citation removal.
- [ ] T008 Add failing API and SQL contract tests for status, checkpoint, review, and publication boundaries.

## Phase 2: State, classification, planning, and graph (P1)

- [ ] T009 Implement typed state and version metadata in `apps/backend/src/atlas/agent/state.py`.
- [ ] T010 Implement deterministic intent/depth/language/risk/freshness classification with safe fallback.
- [ ] T011 Implement bounded question decomposition, source/date criteria, evidence budget, and report path planning.
- [ ] T012 Implement explicit graph orchestration and conditional routes in `apps/backend/src/atlas/agent/orchestration.py`.
- [ ] T013 Add node-level timeout, cancellation, state-isolation, safe-error, and redacted event handling.
- [ ] T014 Integrate existing cited-answer verification and report-spec validation without bypassing their contracts.

## Phase 3: Durable checkpoints and replay (P1)

- [ ] T015 Implement checkpoint repository protocol and deterministic in-memory adapter in `apps/backend/src/atlas/agent/checkpoints.py`.
- [ ] T016 Implement content-safe state serialization, version checks, expiration, and corruption detection.
- [ ] T017 Implement concurrency-safe resume keyed by `thread_id` and replay key with duplicate side-effect suppression.
- [ ] T018 Add PostgreSQL migration `database/migrations/versions/0024_agent_checkpoints_reviews.py` with checkpoint/review/node-event tables, constraints, indexes, and grants.
- [ ] T019 Add SQL contract `database/tests/014_agent_checkpoints_reviews.sql` for uniqueness, expiry, append-only decisions, and tenant isolation.
- [ ] T020 Add crash/resume integration tests for answer, report, ingestion, and evaluation job categories.

## Phase 4: Human review boundary (P1)

- [ ] T021 Implement review request/decision state machine in `apps/backend/src/atlas/agent/review.py`.
- [ ] T022 Enforce reviewer authorization, expiry, decision idempotency, evidence-preserving edits, and rejection terminal states.
- [ ] T023 Add publication guard that accepts only approved/validated review outcomes and never publishes partial artifacts.
- [ ] T024 Add API routes for run status, review request, approve/edit/reject, resume, and safe error responses.
- [ ] T025 Add Spanish/English review panel and pending/approved/edited/rejected states in `apps/web/src/features/agent/ReviewPanel.tsx`.
- [ ] T026 Add Playwright review and resume journeys in `apps/web/tests/e2e/agent-review.spec.ts`.

## Phase 5: Observability, evaluation, and documentation

- [ ] T027 Add route/node/checkpoint/review telemetry with request/run/thread IDs, latency, outcome, versions, and safe error code.
- [ ] T028 Add deterministic evaluation cases for node order, abstention, replay, review gating, and no-secret state.
- [ ] T029 Run targeted/full backend tests, migration/SQL contract, lint, mypy, and browser suite; record `docs/verification/006-agent-graph-human-review.md`.
- [ ] T030 Update README with Feature 006 scope, review workflow, checkpoint guarantees, and verification command.
- [ ] T031 Create `docs/architecture/006-agent-graph-human-review.md` and `docs/adr/0005-explicit-agent-orchestration.md`.
- [ ] T032 Update PRD backlog/status matrix and add documentation task evidence.
- [ ] T033 Run SpecKit Analyze and Converge; append and implement any remaining traceable tasks before closure.

## Dependencies and Execution Order

- Phase 1 blocks all implementation.
- Phase 2 establishes the state and graph consumed by checkpoint and review phases.
- Phase 3 and Phase 4 may proceed in parallel after T009, but publication tests depend on both.
- Phase 5 starts only after all user-story tests are green.

## Requirements Traceability

| Requirement | Implementation | Verification |
|---|---|---|
| FR-AGT-001–005 | T009–T014 | T004–T005, T013 |
| FR-AGT-006 | T014, T021–T024 | T007, T023–T026 |
| FR-AGT-007–008 | T015–T020 | T006, T019–T020 |
| FR-AGT-009 | T021–T026 | T007, T023–T026 |
| FR-AGT-010 | T013, T027 | T005–T008, T029 |
| SC-AGT-001–006 | T009–T033 | T004–T008, T020, T026–T029 |
