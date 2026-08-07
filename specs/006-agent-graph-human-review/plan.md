# Implementation Plan: Agent Graph, Planning, Checkpoints, and Human Review

**Branch**: `codex/006-agent-graph-human-review` | **Date**: 2026-08-06 | **Spec**:
`specs/006-agent-graph-human-review/spec.md`

## Summary

Extend the existing explicit cited-answer workflow into a typed, inspectable orchestration slice.
The first implementation keeps provider calls behind current ports, adds a stable `AtlasState` and
route plan, persists content-safe checkpoints by thread, and introduces a review boundary that can
approve, edit, or reject report/answer publication. Existing evidence, report, privacy, and ingestion
contracts remain authoritative.

## Technical Context

- Python 3.12, FastAPI, Pydantic v2, LangGraph StateGraph, PostgreSQL/Alembic, pytest, mypy, Ruff.
- Existing `CitedAnswerGraph`, answer/report contracts, operator auth, and LangSmith sink are reused.
- Checkpoint records contain hashes/IDs and redacted state summaries, never raw private content or
  secrets. A deterministic in-memory adapter supports tests; PostgreSQL is the durable adapter.
- Review decisions are authorization-checked, expiry-aware, optimistic-concurrency-safe, and
  idempotent by decision key.

## Constitution Check

- Evidence over fluency: route state retains evidence/citation identifiers and verification outcome.
- Spec before code: this feature has a complete spec, plan, and task list before implementation.
- Test/evaluate first: route, replay, checkpoint, and review tests precede implementation.
- Security/privacy: state and telemetry are redacted; untrusted evidence cannot authorize tools.
- Observable/cost-aware: node events carry request/run IDs, node, latency, outcome, and safe error.
- Small vertical slice: deterministic local graph/checkpoint/review path is first; advanced routing is
  deferred to Feature 008.

## Architecture and Data Model

1. `AtlasState` wraps the existing cited-answer state with typed request metadata, route plan,
   checkpoints, review status, and version identifiers.
2. `AgentGraph` classifies, plans, retrieves/verifies, composes, optionally pauses for review, and
   finalizes. Every conditional edge is named and has a safe terminal route.
3. `CheckpointRepository` stores one versioned snapshot per `(thread_id, node, replay_key)` and
   prevents duplicate side effects during concurrent resume.
4. `ReviewService` validates evidence-preserving edits and writes an append-only decision record;
   publication is a separate authorized transition.
5. API routes expose status/checkpoint/review actions without returning private state bodies.

## Project Structure

```text
apps/backend/src/atlas/agent/
├── state.py                 # AtlasState, RoutePlan, versioned state schemas
├── orchestration.py         # classifier/planner and explicit graph routes
├── checkpoints.py           # repository and idempotent resume adapter
└── review.py                # review request/decision state machine
apps/backend/src/atlas/api/routes/agent.py
apps/backend/tests/unit/agent/
apps/backend/tests/integration/agent/
apps/backend/tests/security/test_agent_orchestration.py
database/migrations/versions/0024_agent_checkpoints_reviews.py
database/tests/014_agent_checkpoints_reviews.sql
apps/web/src/features/agent/ReviewPanel.tsx
apps/web/tests/e2e/agent-review.spec.ts
```

## Implementation Sequence

1. Add failing state, routing, checkpoint, replay, review, security, and API contract tests.
2. Implement typed state/classification/planning and explicit deterministic routing.
3. Implement content-safe checkpoint persistence and concurrency/idempotent resume.
4. Implement review approve/edit/reject validation and publication boundary.
5. Wire API/panel, migration and SQL contract; run full regression, browser and eval suites.
6. Update README/ADR/architecture/evidence, then run SpecKit Analyze and Converge before closure.

## Risks and Mitigations

- State bloat: persist references, hashes and bounded summaries rather than source bodies.
- Duplicate publication: require decision keys and transactional status transitions.
- Provider variability: classification/planning fallback is deterministic and provider-neutral.
- Review bypass: only a validated, unexpired authorized decision can enter publication.
