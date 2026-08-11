# Tool Registry Contract v1

## Catalog response

`GET /v1/agent/tools`

Returns a versioned list of available `ToolDefinition` records. The response must be safe for the
requesting identity and locale; it must not include provider secrets, internal prompts, or disabled
connector credentials.

## Plan request

`POST /v1/agent/plans`

```json
{
  "request": "Compare LangGraph and LangChain tool calling",
  "locale": "es-MX",
  "selected_tool": "comparison",
  "input": {"technologies": ["langgraph", "langchain"]}
}
```

The response contains a validated `AgentPlan`, plan hash, risk summary, required approvals, and
expiry. It does not execute a tool.

Plans containing a private or side-effecting tool require an `Idempotency-Key` header. The client
must retain that operation key and send the exact same value when deciding the approval and when
starting or explicitly resuming execution. The server binds the approval decision key to this
operation key; a missing or different value is rejected before an adapter can execute.

## Execute request

`POST /v1/agent/runs`

Execution accepts a plan hash and optional approval IDs. The server revalidates the plan, actor,
scopes, arguments, policy, budgets, and availability before each call.

For private or side-effecting calls, replay protection and the rolling per-visitor/tool quota are
reserved before adapter execution. Exact replays do not consume a second quota unit. Conflicting
key reuse returns `409`; exhausted quota returns `429` with `Retry-After` and a bounded run ID.

## Event/status contract

- `GET /v1/agent/runs/{run_id}` returns safe run status and summary.
- `GET /v1/agent/runs/{run_id}/events` streams ordered events; reconnect uses `after_sequence`.
- `POST /v1/agent/runs/{run_id}/cancel` requests cancellation.
- `POST /v1/agent/runs/{run_id}/resume` resumes from a checkpoint with replay protection.

## Approval contract

`POST /v1/agent/approvals/{approval_id}/decision`

The decision body includes the actor, decision key, and optional edit only for reviewable text. The
server rejects a stale, argument-mismatched, or operation-key-mismatched approval and records the
rejection as an event. The `Idempotency-Key` header is mandatory for this route.
