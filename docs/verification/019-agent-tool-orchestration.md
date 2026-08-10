# Feature 019 verification

Executed on 2026-08-10 from branch `codex/019-agent-tool-orchestration`.

## Local evidence

- Backend planner/provider, agent contracts, policy, event, adapter, boundary, and API tests:
  **55 passed** (12 focused planner/provider/API tests plus 43 agent/security contract tests).
- Ruff on agent/API/observability paths: **passed**.
- Mypy on agent/API/observability paths: **passed**.
- OpenAI planner contract: structured `AgentPlanProposal` parsed from the Responses API with
  model `gpt-5.6-luna`; unknown tools and malformed arguments are rejected by the server catalog.
- Provider outage behavior: `ProviderAdapterError` selects the bounded deterministic proposal;
  provider-specific response objects never cross into the agent layer.
- Bounded executor tests: **4 passed** for per-tool timeout, evidence budget overflow, cancellation
  before the next step, and partial failure without invoking later steps.
- Agent/contract/security regression after executor changes: **28 passed**.
- Read-only adapter/API integration tests: **14 passed**; read-only calls are delegated through the
  adapter boundary, bounded provenance/excerpt/relation fields are preserved, and private/unknown
  tools cannot be registered there.
- The agent `daily_news` path now derives a stable `news:<content_sha256>` evidence reference from
  the reviewed candidate, preserves publisher/URL/capture metadata in the bounded adapter result,
  and abstains cleanly when no previous-day candidate exists.
- Side-effect adapter/policy tests: **48 passed** in the focused policy/agent/contract run;
  approval mismatch, bound-target mismatch, missing approval, missing consent, anonymous access,
  ownership denial, and handler errors remain non-mutating. The API contract now records rejected
  side-effect calls as failed tool events instead of treating them as successful completions.
- PostgreSQL persistence contract tests: **10 passed** for plan round-trip, ordered event reconnect,
  checkpoint integrity/replay conflict, cross-repository checkpoint claim, and approval/tool-call
  round-trips, atomic event-lock ordering, durable run-actor persistence, and terminal-run replay
  protection. The non-development runtime selects these adapters, and API execution records each
  tool call after the run exists.
- Idempotency contract tests: **5 passed** for plan/run replay and conflicting-key rejection. The
  non-development store is now PostgreSQL-backed and scoped by an opaque visitor hash; durable saves
  use the unique scope/key constraint as the concurrent-write guard. The migration still needs to
  be applied to the hosted project before production activation.
- Deterministic gate: `scripts/verify-agent-tools.ps1` passed with **47 tests**, Ruff/mypy across
  **21 files**, and all **5** dataset cases.
- `scripts/verify-agent-tools.ps1`: **passed**, 5 deterministic evaluation cases.
- Frontend TypeScript and lint on modified agent files: **passed**.
- Playwright `tests/e2e/agent-workspace.spec.ts`: **1 passed**.

## Supabase evidence

Migration `0028_agent_tool_orchestration` was applied to project `fcbclsaytbjpywlaplbh` through the
Supabase MCP migration tool. The repository files `0029_agent_idempotency.py` and
`0030_agent_checkpoint_claims.py` are applied remotely under the migration names
`agent_idempotency` and `agent_checkpoint_claims`; the remote list reports 30 revisions and the
`atlas` schema contains `agent_idempotency_records` and `agent_checkpoint_claims`.
The SQL grants revoke public access and grant only the existing `atlas_worker`/`atlas_readonly`
roles. No user or private document data was seeded.

The repository now contains migration `0031_agent_tool_rls.py` plus SQL contract
`database/tests/015_agent_tool_rls.sql` for the seven durable agent tables. The hosted MCP rejected
automatic application because `FORCE RLS` and global worker/read-only policies require explicit
owner approval of the access design. The remote project therefore remains at 30 revisions; this is
an intentional pending deployment gate, not a claim that hosted RLS is complete. The Supabase
security advisor also still reports the project-wide RLS-disabled lint for the other private
`atlas` tables.

## Remaining honest gaps

Cross-process idempotency/replay claims, complete read-only evidence envelopes, durable owner
scoping for every lifecycle endpoint, checkpoint-aware tool resume, RLS policy design, live
provider traces, latency/cost measurements, and production deployment evidence remain open under
Feature 018/019 tasks. Feature 019 remains open until those mandatory tasks and convergence evidence
are complete.
