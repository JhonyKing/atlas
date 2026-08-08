# Feature 019 — agent tool orchestration

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
request → planner (GPT-5.6 Luna label) → typed plan → policy/approval gate
       → bounded domain adapter → ordered safe events → evidence/artifact references
```

The API surface is `/v1/agent/tools`, `/v1/agent/plans`, `/v1/agent/runs`, the event reconnect
endpoint, explicit cancel/resume endpoints, and the approval decision endpoint. The local adapter
is intentionally deterministic when a provider service is unavailable; it abstains instead of
pretending that a tool ran.

## Persistence and observability

Migration `0028_agent_tool_orchestration` adds private-schema tables for plans, runs, tool calls,
ordered events, and approvals. The current local repository is an in-memory adapter with the same
contract; production wiring to the managed repository remains a deployment task. LangSmith receives
only bounded tags and scalar metadata (plan hash, run ID, locale, tool count, budgets, and outcome),
never question text or tool arguments.

## Evidence

- `evals/datasets/agent_tool_orchestration.jsonl`
- `scripts/verify-agent-tools.ps1`
- `docs/verification/019-agent-tool-orchestration.md`
- `specs/019-agent-tool-orchestration/tasks.md`
