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
- Side-effect adapter/policy tests: **47 passed** in the focused policy/agent/contract run;
  approval mismatch, missing approval, anonymous access, ownership denial, and handler errors
  remain non-mutating.
- PostgreSQL persistence contract tests: **5 passed** for plan round-trip, ordered event reconnect,
  checkpoint integrity/replay conflict, and approval/tool-call round-trips. The non-development
  runtime selects these adapters, and API execution records each tool call after the run exists.
- Idempotency contract tests: **5 passed** for plan/run replay and conflicting-key rejection. The
  non-development store is now PostgreSQL-backed and scoped by an opaque visitor hash; the new
  migration still needs to be applied to the hosted project before production activation.
- Deterministic gate: `scripts/verify-agent-tools.ps1` passed with **35 tests**, Ruff/mypy across
  **21 files**, and all **5** dataset cases.
- `scripts/verify-agent-tools.ps1`: **passed**, 5 deterministic evaluation cases.
- Frontend TypeScript and lint on modified agent files: **passed**.
- Playwright `tests/e2e/agent-workspace.spec.ts`: **1 passed**.

## Supabase evidence

Migration `0028_agent_tool_orchestration` was applied to project `fcbclsaytbjpywlaplbh` through the
Supabase MCP migration tool. The repository now includes `0029_agent_idempotency`; it is not yet
reported by the remote migration list. Once applied, the `atlas` schema will also contain
`agent_idempotency_records`.
The SQL grants revoke public access and grant only the existing `atlas_worker`/`atlas_readonly`
roles. No user or private document data was seeded.

The Supabase security advisor still reports the project-wide informational/critical RLS-disabled
lint for private `atlas` tables. This is not auto-remediated: enabling RLS without explicit policies
would block worker access. The existing migrations revoke public privileges; a production policy
review remains a deployment gate.

## Remaining honest gaps

Cross-process idempotency/replay claims, live provider traces, latency/cost measurements, and
production deployment evidence remain open under Feature 018/019 tasks. Feature 019 remains open
until those mandatory tasks and convergence evidence are complete.
