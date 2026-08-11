# Feature 019 verification

Executed on 2026-08-11 and finalized from integration branch `codex/main-integration`.

## Final T038 promotion gate (2026-08-11)

- Complete backend suite: **428 passed, 4 conditionally skipped, 0 failed**.
- Python quality gates: Ruff passed; strict mypy passed across **183 source files**.
- Deterministic agent-tool gate: **58 tests passed**, Ruff/mypy passed across its focused paths,
  and all **5/5** fixture cases passed.
- Web quality gates: TypeScript passed, ESLint passed, and **35/35** Vitest tests passed.
- Chromium browser matrix: **149 passed, 4 deployment-only tests skipped, 0 failed** across
  localized routes, public journeys, private-data states, agent workspace, route-state QA and the
  375/390/768/1024/1280/1440/1920 px viewport matrix. The four skipped tests require hosted
  `ATLAS_DEPLOYMENT_WEB_ORIGIN`/`ATLAS_DEPLOYMENT_API_ORIGIN` and belong to Feature 018's
  post-deployment smoke gate.
- Next.js 16.2.12 production build with Webpack: passed; all static and dynamic routes compiled,
  typechecked and generated successfully.
- The first full browser pass exposed two stale-locale upload messages. The component was changed
  to store semantic `accepted`/`rejected` state and translate during render; the focused 3/3 account
  rerun and the final 149-test matrix passed.
- Playwright reported a non-blocking hydration warning for an injected
  `style="caret-color: transparent"` attribute on one report input. No matching source/test code
  exists in the repository and every report, route-state and viewport journey passed; it is kept as
  an environment warning rather than represented as an application defect.

This closes T038 and Feature 019's implementation/verification scope. Hosted deployment smoke and
production API readiness remain Feature 018 responsibilities and can run only after integration.

## Local evidence

- Backend planner/provider, agent contracts, policy, event, adapter, boundary, and API tests:
  **56 passed** (12 focused planner/provider/API tests plus 44 agent/security contract tests).
- Ruff on agent/API/observability paths: **passed**.
- Mypy on agent/API/observability paths: **passed**.
- OpenAI planner contract: structured `AgentPlanProposal` parsed from the Responses API with
  model `gpt-5.6-luna`; unknown tools and malformed arguments are rejected by the server catalog.
- Provider outage behavior: `ProviderAdapterError` selects the bounded deterministic proposal;
  provider-specific response objects never cross into the agent layer.
- Bounded executor tests: **4 passed** for per-tool timeout, evidence budget overflow, cancellation
  before the next step, and partial failure without invoking later steps.
- API execution now applies each catalog tool's `timeout_ms`; an explicit
  `POST /v1/agent/runs/{run_id}/resume?execute=true` continues pending steps while durable
  completed-call records and per-step checkpoints prevent duplicate tool invocation.
- Agent/contract/security regression after executor changes: **28 passed**.
- Read-only adapter/API integration tests: **14 passed**; read-only calls are delegated through the
  adapter boundary, bounded provenance/excerpt/relation fields are preserved, and private/unknown
  tools cannot be registered there.
- Side-effect results now use the same bounded evidence envelope and preserve only typed provenance,
  excerpts, relations, source versions, artifact IDs, and artifact links; arbitrary handler fields
  are dropped. The complete domain-result envelope remains open under T045.
- The agent `daily_news` path now derives a stable `news:<content_sha256>` evidence reference from
  the reviewed candidate, preserves publisher/URL/capture metadata in the bounded adapter result,
  and abstains cleanly when no previous-day candidate exists.
- Side-effect adapter/policy tests: **48 passed** in the focused policy/agent/contract run;
  approval mismatch, bound-target mismatch, missing approval, missing consent, anonymous access,
  ownership denial, and handler errors remain non-mutating. The API contract now records rejected
  side-effect calls as failed tool events instead of treating them as successful completions.
- PostgreSQL persistence contract tests: **11 passed** for plan round-trip, ordered event reconnect,
  checkpoint integrity/replay conflict, cross-repository checkpoint claim, and approval/tool-call
  round-trips, atomic event-lock ordering, durable run-actor persistence, and terminal-run replay
  protection. The non-development runtime selects these adapters, and API execution records each
  tool call after the run exists.
- PostgreSQL persistence contract suite now totals **12 passed**; the added cross-repository test
  proves a second repository instance can read the same terminal run and ordered event stream,
  complementing the checkpoint claim test for replay-safe worker handoff.
- Idempotency contract tests: **5 passed** for plan/run replay and conflicting-key rejection. The
  non-development store is now PostgreSQL-backed and scoped by an opaque visitor hash; durable saves
  use the unique scope/key constraint as the concurrent-write guard. The migration still needs to
  be applied to the hosted project before production activation.
- Durable run checkpoints are now persisted after each tool result with a stable per-step replay key
  (`agent-run:<plan_hash>:step-N`). The contract replay test recovers the checkpoint and confirms
  that repeating the run returns the original event stream without another tool call. Full
  checkpoint-aware resume of pending steps is now explicitly opt-in through
  `POST /v1/agent/runs/{run_id}/resume?execute=true`; approval IDs and consent remain explicit,
  while the default acknowledgement path stays backwards compatible.
- Deterministic gate: `scripts/verify-agent-tools.ps1` passed with **50 tests**, Ruff/mypy across
  **21 files**, and all **5** dataset cases.
- `scripts/verify-agent-tools.ps1`: **passed**, 5 deterministic evaluation cases.
- Frontend TypeScript and lint on modified agent files: **passed**.
- Historical Playwright baseline `tests/e2e/agent-workspace.spec.ts`: **1 passed**; the current
  rerun is recorded below and is not claimed because the local harness did not hydrate the catalog.

### Live trace evidence (2026-08-11)

The opt-in exporter `scripts/export-agent-live-evidence.py` ran six local API journeys through
the configured LangSmith-compatible sink: successful, abstained, rejected, failed, cancelled,
and resumed. The artifact is
`evals/results/agent-tool-live-evidence-20260811.json` and contains six opaque trace/run IDs,
HTTP status, measured wall-clock latency, lifecycle outcome, trace count, and safe trace fields
(plan hash, model, locale/corpus labels, approval flag, and provider token/cost values when
reported). It contains no question text, tool arguments, excerpts, private resource identifiers,
or model inputs/outputs. All six cases produced at least one trace (`status: passed`).

The lifecycle contract test `test_cancel_and_resume_emit_content_free_lifecycle_traces` also
asserts numeric latency and explicit `cancelled`/`resumed` terminal trace statuses. The separate
opt-in LangSmith connectivity smoke passed (**1 passed**).

This historical focused-live-evidence section did not claim the full browser suite at the time it
was produced. The later final T038 promotion gate above supersedes that limitation; only the four
hosted deployment journeys remain intentionally deferred to Feature 018.

### Browser/build harness correction (2026-08-11)

The local harness failure was traced to Next 16 Turbopack root inference plus the system Node
20/pyenv wrapper used by the Playwright web server. The web app now pins the application root,
Playwright starts the same `process.execPath` as the test runner with Webpack, and the Vercel/web
build command uses `next build --webpack`. Evidence: production build generated all 12 routes;
the agent workspace journey passed **1/1** and the AppShell/locale/route contract passed **4/4**.
The later final T038 run completed the full 153-test matrix with **149 passed and 4 hosted
deployment-only tests skipped**; there were no browser failures.

### Read-only evidence envelope evidence (2026-08-11)

The agent run route now persists a normalized `tool_results` envelope in `agent_runs.output` and
returns it in the completed-run response. The envelope is bounded by the same adapter allowlist,
so provenance, source versions, excerpts, typed evidence relations, artifact IDs, and artifact
links can be inspected without exposing provider-specific objects or unbounded content. Queued
answer, comparison, and report jobs expose safe status/download links; daily news preserves its
publisher, canonical URL, capture time, and bounded excerpt; corpus status preserves its snapshot
and generation provenance plus the canonical `/v1/corpus` link. The focused contract/adapters suite
passed **15 tests**, and the complete backend gate passed **56 tests**, Ruff, and mypy.

### Session-backed scope gate evidence (2026-08-11)

The side-effect adapter now receives scopes resolved from the validated request session boundary:
every caller has the explicit `anonymous` scope, while `authenticated` is added only when the
validated subject matches the requested actor. A private or mutating tool therefore cannot run
merely because a caller supplied an actor ID, approval ID, consent flag, or ownership-shaped
argument. Missing required scopes are rejected before the ownership callback or handler is reached.
The focused adapter/route suite includes regressions proving that the owner check is not invoked
for an anonymous caller with an approved private-delete plan.

### Operation-key binding and quota closure (2026-08-11)

Private and side-effecting plans now require one operation-level `Idempotency-Key`. That exact key
is cryptographically included in the durable approval decision key and must be reused for approval
and run requests. Missing keys fail with `400`; mismatched keys fail with `403`; a conflicting
replay fails with `409`. The web client retains the plan operation key and reuses it for the full
journey instead of generating unrelated keys per request.

Before a private or mutating adapter executes, ATLAS rechecks approval, session-backed scope and
consent, then reserves a per-visitor/tool rolling quota. Development uses a lock-protected
repository; non-development runtimes use the existing PostgreSQL
`atlas.agent_idempotency_records` ledger under an advisory transaction lock. Exact replays return
the original reservation without consuming another unit. Exhaustion records a rejected tool call,
emits `tool_call.failed`, returns `429` plus `Retry-After`, and does not call the adapter.

Evidence: **66** focused agent and agent-contract tests passed, including the approval-key and
quota contract; **7** focused policy/quota unit tests passed; Ruff passed; strict mypy passed for
**183 source files**; web typecheck and ESLint passed; **35/35** web tests passed. This closes T043.

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

### Owner-approved RLS follow-up (2026-08-11)

The owner then approved and the hosted MCP applied `agent_tool_rls` in production. Verification
found 31 remote revisions, seven durable agent tables with FORCE RLS, 14 worker/read-only
policies, and no `anon`/`authenticated` grants on those tables. This closes T049 for the Agent
Tool slice. The remaining 41 `atlas` tables without RLS remain a separate project-wide backlog.
Evidence: `evals/results/supabase-migration-agent-tool-rls-20260811-applied.json`.

## Remaining honest gaps

Production deployment evidence remains open under Feature 018. Cross-process replay, quota/scope
policy enforcement, approval-key binding, and read-only evidence envelopes are covered by the
durable repository and route contract tests.
Agent-tool RLS for the seven durable tables is verified; the separate project-wide 41-table RLS
backlog remains open. Feature 019 remains open only until its complete verification task T038 is
executed and recorded.
