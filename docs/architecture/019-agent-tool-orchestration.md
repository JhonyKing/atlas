# Feature 019 - agent tool orchestration

ATLAS exposes a bounded agent surface rather than allowing an LLM to invoke arbitrary code. The
planner produces a finite `AgentPlan`; the server validates it against the versioned catalog,
normalizes arguments, calculates a plan hash, and only then executes an allowlisted tool.

## Trust boundaries

1. Natural-language text and model output are untrusted input.
2. `ToolCatalog` is the only authority for tool IDs, versions, schemas, scopes, side effects,
   budgets, timeouts, and availability.
3. `validate_plan` rejects unknown tools, schema violations, dependency cycles, expired plans, and
   budget overflow before execution.
4. Private or consequential tools create an approval bound to actor, tool/version, normalized
   arguments, target, plan, and expiry. The run remains `awaiting_approval` until the owner submits
   the decision key.
5. Domain adapters return bounded evidence/artifact identifiers; they never expose raw provider
   responses, credentials, private document bodies, or arbitrary URLs.

## Runtime flow

```text
request -> Responses planner (GPT-5.6 Luna) -> AgentPlanProposal
        -> catalog/schema validation -> policy/approval gate
        -> bounded domain adapter -> ordered safe events -> evidence/artifact references
```

When the provider is unavailable, the planner uses the deterministic proposal function. This is an
explicit fallback mode; it never fabricates provider success and it still passes through the same
catalog and plan validation path.

The executor invokes only registered catalog handlers. Each call is bounded by the catalog timeout
and the plan call/evidence budgets. A timeout, handler failure, or budget overflow records a safe
failure event and stops the remaining plan; a cancellation before the next step records a terminal
cancelled event without replaying the completed calls.

Read-only API runs pass through `ReadOnlyToolAdapters` before invoking answer, comparison, report,
news, or corpus services. The adapter copies arguments, bounds evidence/artifact references, and
redacts provider/handler exceptions to a stable result envelope.

Side-effect adapters are separate. `SideEffectToolAdapters` requires a matching, unexpired
approval bound to the plan, actor, tool version, and normalized arguments, then checks authenticated
ownership for private tools before invoking a handler. Missing approval, ownership denial, or
handler failure produces a safe non-mutating result.

Plan, run, and approval endpoints accept an `Idempotency-Key`. The current local replay store
returns the original response for the same fingerprint and rejects a conflicting reuse with 409;
durable cross-instance idempotency and quota/consent convergence remain open.

The API surface is `/v1/agent/tools`, `/v1/agent/plans`, `/v1/agent/runs`, the event reconnect
endpoint, explicit cancel/resume endpoints, and the approval decision endpoint.

## Persistence and observability

Migration `0028_agent_tool_orchestration` adds private-schema tables for plans, runs, tool calls,
ordered events, and approvals. The current local repository is an in-memory adapter with the same
contract; the PostgreSQL adapter now persists plans, runs, ordered events, and checkpoints for
non-development runtimes. Durable tool-call/approval rows and cross-process replay claims remain
open convergence work. LangSmith receives only bounded tags and scalar metadata (plan hash, run ID,
locale, tool count, budgets, and outcome), never question text or tool arguments.

## Evidence

- `evals/datasets/agent_tool_orchestration.jsonl`
- `scripts/verify-agent-tools.ps1`
- `docs/verification/019-agent-tool-orchestration.md`
- `docs/verification/019-speckit-analysis.md`
- `specs/019-agent-tool-orchestration/tasks.md`
