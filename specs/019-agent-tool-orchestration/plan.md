# Implementation Plan: Agent Tool Orchestration

**Branch**: `019-agent-tool-orchestration` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

## Summary

Add a typed agent control plane that presents ATLAS capabilities as an allowlisted tool catalog,
validates plans, gates private/mutating calls with approval and ownership, executes bounded plans,
streams safe lifecycle events, preserves evidence/artifacts, and exposes a localized agent
workspace. Existing feature services remain the domain implementations; the agent adds orchestration
and policy seams around them.

## Technical Context

**Language/Version**: Python 3.13, Node 24, strict TypeScript

**Primary Dependencies**: FastAPI/Pydantic, existing provider adapter/Responses API, existing
LangGraph/checkpoint/review seams, Next.js/React, LangSmith/OpenTelemetry

**Storage**: Existing PostgreSQL event/run/checkpoint/policy tables and in-memory test doubles;
versioned migrations for durable run events, plans, approvals, and idempotency records

**Testing**: pytest contract/unit/integration/security, Vitest, Playwright, deterministic agent/eval
fixtures, optional live LangSmith/provider evidence

**Target Platform**: Existing local Docker/API/web now; deployment adapter is Feature 018

**Project Type**: Monorepo web application, API, agent orchestrator, and evaluation harness

**Performance Goals**: Plan validation p95 <250 ms without provider calls; event delivery within 1 s
of state change in local tests; preserve existing answer/comparison/report/news SLO instrumentation

**Constraints**: No arbitrary code/URL tools; model output is untrusted; strict schemas; bounded
plans; explicit approvals; no secrets/private content in events/traces; existing endpoints remain
compatible during migration

**Scale/Scope**: First slice supports finite plans and the current ATLAS capabilities; no open-ended
autonomous loops or multi-tenant workflow scheduler

## Constitution Check

- Evidence Over Fluency: PASS - tool results preserve evidence IDs and verification/abstention contracts.
- Spec Before Code: PASS - spec, checklist, plan, contracts, quickstart, and tasks precede implementation.
- Test and Evaluate First: PASS - invalid calls, safety, evidence mapping, replay, and quality gates begin as tests.
- Explicit Contracts and Type Safety: PASS - registry, plan, event, approval, and result schemas are versioned.
- Provider Independence with Measured Routing: PASS - planner uses existing provider adapter and Luna default without leaking provider objects.
- Security and Privacy by Design: PASS - allowlist, scopes, ownership, approval, idempotency, redaction, and prompt-injection tests are required.
- Observable and Cost-Aware: PASS - each run has event/trace correlation, latency, token, cost, model, and outcome fields.
- Small Vertical Slices Before Scale: PASS - finite plans and existing capabilities first; arbitrary autonomy is excluded.
- English-Canonical Engineering: PASS - IDs/schemas/docs are English; UI copy is localized.

## Project Structure

```text
specs/019-agent-tool-orchestration/       # feature decision record
apps/backend/src/atlas/agent/             # registry, planner, policy, executor, events
apps/backend/src/atlas/api/routes/agent.py # catalog/plan/run/approval/cancel/resume contracts
apps/backend/tests/agent/                  # contract, safety, lifecycle, evaluation tests
apps/web/src/features/agent/               # catalog, workspace, approval, timeline UI
database/migrations/                       # durable run/plan/call/event/approval records
scripts/                                   # deterministic agent verification and evidence export
docs/architecture/                         # ADR and tool-trust boundary
docs/runbooks/                             # operator/debugging guidance
```

**Structure Decision**: Extend the existing `atlas.agent` and agent API route instead of adding a
second orchestration package. Feature adapters call existing domain services through narrow ports.

## Implementation Sequence

1. Add failing registry, schema, policy, approval, event, and evidence-mapping tests.
2. Implement versioned tool definitions and catalog endpoint with localization metadata.
3. Implement plan validation, model proposal adapter, dependency/budget checks, and fail-closed policy.
4. Implement bounded executor, durable events, checkpoint/replay/cancel, idempotency, and tool adapters.
5. Add run/approval/cancel/resume API contracts and localized agent workspace/timeline.
6. Add LangSmith/OpenTelemetry tags/redaction, deterministic evaluation, live evidence hooks, and docs.
7. Run Speckit analyze/converge, update README/ADR/status, and commit each vertical slice.

## Complexity Tracking

| Item | Why needed | Simpler alternative rejected because |
|---|---|---|
| Durable ordered run events | UI resume, audit, LangSmith correlation, and portfolio evidence need lifecycle visibility | A final response-only record cannot explain tool decisions or replay safety |
| Separate approval/idempotency records | Mutation/private tools must be authorized and repeat-safe | A boolean approval flag is not bound to actor/arguments/target |
