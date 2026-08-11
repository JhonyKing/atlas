# Tasks: Agent Tool Orchestration

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/)

**Prerequisites**: Feature 006 agent/checkpoint/review contracts, Feature 013 observability seams,
Feature 016 evaluation harness, and Feature 018 deployment contracts remain available.

## Phase 1: Failing contracts and safety tests (P1)

- [X] T001 [US1] Add registry/catalog schema tests for IDs, versions, localized copy, input/output schemas, scopes, side-effect level, approval, timeout, budget, and availability in `apps/backend/tests/agent/test_tool_registry.py`.
- [X] T002 [US2] Add plan-validation tests for explicit selection, natural-language proposal, unknown tool, malformed arguments, dependency cycle, disabled tool, budget overflow, and timeout in `apps/backend/tests/agent/test_plan_validation.py`.
- [X] T003 [US3] Add approval/policy tests for actor, scope, ownership, consent, expiry, normalized argument hash, target, and idempotency replay in `apps/backend/tests/agent/test_tool_policy.py`.
- [X] T004 [US2] Add evidence/artifact mapping tests proving answer, comparison, report, news, and corpus results preserve IDs, provenance, bounded excerpts, relations, and abstention in `apps/backend/tests/agent/test_tool_results.py`.
- [X] T005 [US4] Add ordered event lifecycle, reconnect, cancellation, failure, and resume tests in `apps/backend/tests/agent/test_run_events.py`.
- [X] T006 [US2] Add prompt-injection/security tests proving source/tool text cannot authorize tools, reveal secrets, bypass approval, or widen scopes in `apps/backend/tests/security/test_agent_tool_boundaries.py`.
- [X] T007 [US1] Add browser tests for localized catalog, tool selection, input forms, unavailable states, run timeline, evidence/artifact links, and approval cards in `apps/web/tests/e2e/agent-workspace.spec.ts`.

## Phase 2: Registry and typed contracts (P1)

- [X] T008 [US1] Define versioned `ToolDefinition`, input/output, policy, availability, and localization schemas in `apps/backend/src/atlas/agent/tools/schemas.py`.
- [X] T009 [P] [US1] Implement the allowlisted registry with the initial answer/comparison/report/news/corpus/private/review definitions in `apps/backend/src/atlas/agent/tools/registry.py`.
- [X] T010 [US1] Implement catalog filtering by identity, locale, beta availability, and provider readiness in `apps/backend/src/atlas/agent/tools/catalog.py`.
- [X] T011 [US1] Add `GET /v1/agent/tools` typed route and OpenAPI contract in `apps/backend/src/atlas/api/routes/agent.py` and `apps/backend/src/atlas/api/contracts.py`.
- [X] T012 [P] [US1] Add localized tool labels, descriptions, validation messages, and side-effect/approval copy in `apps/web/src/features/agent/i18n.ts`.

## Phase 3: Planning and authorization (P1)

- [X] T013 [US2] Implement normalized argument validation, plan hash, finite dependency validation, budget, timeout, and expiry in `apps/backend/src/atlas/agent/planning.py`.
- [X] T014 [US2] Integrate GPT-5.6 Luna as the default planner through the existing provider adapter; parse model output into the typed plan and reject provider-specific objects in `apps/backend/src/atlas/agent/planner.py`.
- [X] T015 [US3] Implement scope/ownership/consent/approval policy evaluation and redacted policy reasons in `apps/backend/src/atlas/agent/policy.py`.
- [X] T016 [US3] Add approval and idempotency persistence/migration in `database/migrations/versions/` and repositories in `apps/backend/src/atlas/persistence/agent_runs.py`.
- [X] T017 [US2] Add `POST /v1/agent/plans` and `POST /v1/agent/approvals/{approval_id}/decision` with stale-plan/argument mismatch checks in `apps/backend/src/atlas/api/routes/agent.py`.

## Phase 4: Execution, tools, and durable events (P1)

- [X] T018 [US2] Implement bounded executor with sequential dependencies, per-tool timeout/budget, cancellation, safe partial failure, and no arbitrary code/URL execution in `apps/backend/src/atlas/agent/executor.py`.
- [X] T019 [P] [US2] Implement read-only adapters for cited answer, comparison, report, daily news, and corpus status in `apps/backend/src/atlas/agent/tools/read_only.py`.
- [X] T020 [P] [US3] Implement private-resource, private-upload, private-delete, and human-review adapters with ownership/approval gates in `apps/backend/src/atlas/agent/tools/side_effects.py`.
- [ ] T021 [US2] Implement durable run/plan/call/event/checkpoint persistence, sequence checks, and replay-safe resume in `apps/backend/src/atlas/persistence/agent_runs.py` and `apps/backend/src/atlas/agent/checkpoints.py`.
- [X] T022 [US4] Emit typed lifecycle events with safe payloads and evidence/artifact references in `apps/backend/src/atlas/agent/events.py`.
- [X] T023 [US2] Add `POST /v1/agent/runs`, `GET /v1/agent/runs/{run_id}`, event streaming/reconnect, cancellation, and resume routes in `apps/backend/src/atlas/api/routes/agent.py`.

## Phase 5: Agent workspace UI (P1)

- [X] T024 [US1] Implement catalog and tool-selection workspace in `apps/web/src/features/agent/AgentWorkspace.tsx`.
- [X] T025 [US1] Implement schema-driven input forms and explicit selected-tool/plan preview in `apps/web/src/features/agent/ToolInputForm.tsx`.
- [X] T026 [US3] Implement approval card showing exact tool/version, normalized target, argument summary, expiry, risk, and approve/reject actions in `apps/web/src/features/agent/ApprovalCard.tsx`.
- [X] T027 [US4] Implement reconnectable run timeline, event statuses, evidence/artifact links, cancellation, and resume controls in `apps/web/src/features/agent/RunTimeline.tsx`.
- [X] T028 [US1] Integrate the agent workspace into the localized root page while retaining standalone compatibility entry points in `apps/web/src/app/page.tsx` and `apps/web/src/i18n/index.ts`.
- [X] T029 [US1] Remove hard-coded fake review IDs/evidence IDs from the agent UI and use the real catalog/run/approval APIs in `apps/web/src/features/agent/ReviewPanel.tsx`.

## Phase 6: Observability and evaluation (P2)

- [X] T030 [US4] Add LangSmith/OpenTelemetry run/tool tags for run ID, tool ID/version, model, locale, corpus, latency, tokens, cost, and outcome with redaction in `apps/backend/src/atlas/observability/`.
- [X] T031 [US4] Add deterministic agent evaluation dataset for selection, arguments, evidence mapping, abstention, safety, approval, replay, latency, cost, and artifact correctness in `evals/datasets/agent_tool_orchestration.jsonl`.
- [X] T032 [US4] Add evaluation command and promotion gate that distinguishes deterministic fixture mode from live provider/LangSmith mode in `scripts/verify-agent-tools.ps1` and `apps/backend/src/atlas/evaluation/`.
- [ ] T033 [US4] Add live trace/evidence export for representative successful, abstained, rejected, failed, cancelled, and resumed runs without embedding private content in `evals/results/`.

## Phase 7: Documentation and convergence

- [X] T034 [P] Update `docs/architecture/019-agent-tool-orchestration.md` and add an ADR for registry, trust boundaries, approval, events, and domain adapters.
- [X] T035 [P] Update `README.md` with the agent workspace, tool catalog, local quickstart, demo journey, and evidence links.
- [X] T036 [P] Update `docs/product/feature-status-matrix.md` and PRD traceability with Feature 019 and the mapping from existing features to tools.
- [X] T037 Run Speckit analyze after task generation and resolve critical gaps/contradictions before implementation.
- [ ] T038 Run full lint/typecheck/unit/integration/security/browser and deterministic evaluation gates; record evidence for each user story.
- [X] T039 Run Speckit converge after implementation and keep the feature open while mandatory tests, live evidence, or documentation remain pending.
- [ ] T040 Commit focused vertical slices and update README/ADR/evidence after each completed feature increment.

## Dependencies & Execution Order

- T001-T007 are failing contracts and block implementation.
- T008-T012 establish registry and catalog contracts and block planning/execution.
- T013-T017 establish validated plans and policy/approval and block side effects.
- T018-T023 establish execution/events/API and block the full workspace.
- T024-T029 provide the P1 user workspace and depend on the API contracts.
- T030-T033 depend on event/executor behavior and provide portfolio evidence.
- T034-T040 close only after all required implementation, tests, evaluation, and docs are complete.

## Definition of Done

Feature 019 is complete only when all capabilities are represented in the versioned catalog, the
agent can plan and execute bounded read-only flows, side effects/private actions require valid
approval and ownership, events/checkpoints/replay are safe, UI and API are localized/typed,
evidence/artifacts remain traceable, LangSmith traces are redacted, evaluations pass, and README/
ADR/status documentation reflects the actual implementation. A menu over isolated LLM calls is not
enough to close the feature.

## Phase 8: Convergence

- [X] T041 [US3] Wire a managed Postgres `AgentRunRepository` to migration `0028_agent_tool_orchestration` and use it for production plan/run/call/event/approval persistence (FR-006, FR-008).
- [X] T042 [US2] Connect `AgentPlanner` to the existing provider adapter for GPT-5.6 Luna proposals, parse the provider response into the typed plan, and preserve deterministic fallback mode (FR-013; partial).
- [ ] T043 [US3] Add an explicit idempotency key to plan/run/approval requests and enforce ownership, scope, quota, consent, and replay protection before any private or mutating adapter can execute (FR-006, FR-007; partial).
- [X] T044 [US2] Enforce per-tool timeout and checkpoint-aware resume so cancellation/reconnect never replays a completed tool call (FR-008, SC-007; implemented in the bounded executor and API route, with durable checkpoint/replay contract coverage).
- [ ] T045 [US2] Complete read-only result adapters so answer, comparison, report, news, and corpus outputs preserve provenance, source versions, bounded excerpts, typed evidence relations, and artifact links (FR-005, FR-009; partial).
- [ ] T046 [US4] Run and export representative live LangSmith/evidence traces for successful, abstained, rejected, failed, cancelled, and resumed runs with measured latency, token, cost, locale, corpus, and outcome fields (FR-014, FR-015, SC-006; missing).

## Phase 9: Convergence

- [X] T047 [US4] Make PostgreSQL run-event sequence allocation atomic per run so concurrent workers cannot compute the same `max(sequence) + 1` and violate ordered lifecycle delivery (FR-010, SC-005; implemented and covered by focused persistence tests).
- [X] T048 [US3] Persist the authenticated `actor_id` from plan/run requests into durable agent runs and enforce the same owner scope when loading durable runs and approvals after a restart (FR-006, FR-007; implemented and covered by focused persistence/API tests).
- [X] T049 [US3] Add a reviewed migration and verification evidence for RLS policies that prevent anon/authenticated access to private agent plans, runs, approvals, tool calls, events, idempotency records, and checkpoint claims while preserving the worker path (Constitution VI, FR-006). Evidence: `evals/results/supabase-migration-agent-tool-rls-20260811-applied.json`.
