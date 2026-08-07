# Data Model: Agent Tool Orchestration

## ToolDefinition

| Field | Type | Rules |
|---|---|---|
| `tool_id` | identifier | English-canonical, stable, allowlisted |
| `version` | semver | Changes when input/output or policy changes |
| `input_schema` | schema | Strict; rejects unknown fields |
| `output_schema` | schema | Strict; includes evidence/artifact references where relevant |
| `scopes` | list | Required identity/policy scopes |
| `side_effect_level` | enum | `read`, `private_read`, `mutate`, `publish`, `delete` |
| `approval` | enum | `none`, `explicit_user`, `human_reviewer` |
| `timeout_ms` | integer | Positive bounded value |
| `budget` | object | Tool-call, token, cost, and evidence bounds |
| `availability` | enum | `enabled`, `disabled`, `provider_unavailable`, `quota_exhausted` |
| `localization` | object | `en-US` and `es-MX` display strings |

## AgentPlan

- `run_id`
- `request`
- `locale`
- `steps[]`: tool ID, version, normalized arguments, dependencies, expected output
- `risk_summary`
- `budget`
- `expires_at`
- `plan_hash`

Plans are immutable after authorization. A changed argument or tool version requires a new plan and
approval.

## ToolCall

- `call_id`, `run_id`, `step_id`
- `tool_id`, `tool_version`
- `actor_id`, `scope_snapshot`
- `arguments_hash`, `normalized_arguments` (redacted in logs)
- `idempotency_key`
- `status`: `proposed`, `awaiting_approval`, `approved`, `running`, `completed`, `abstained`,
  `failed`, `cancelled`, `rejected`, `expired`
- `evidence_ids`, `artifact_ids`
- `started_at`, `completed_at`, `latency_ms`, `estimated_cost`

## Approval

- `approval_id`, `run_id`, `call_id`, `actor_id`
- `tool_id`, `tool_version`, `arguments_hash`, `target_resource`
- `decision`: `approved`, `rejected`, `expired`
- `decision_key`, `expires_at`, `created_at`

Approval is accepted only when actor, call, tool/version, argument hash, target, and expiry match.

## AgentRunEvent

- `sequence`, `run_id`, `event_type`, `occurred_at`, `correlation_id`
- `tool_id`/`call_id` when relevant
- safe status summary, evidence/artifact IDs, error category, trace ID

Events are append-only and sequence-checked. A replay resumes from a checkpoint and does not replay
completed side effects.

## AgentRun

Contains request, locale, plan, calls, checkpoint, final status, safe output, evidence/artifact
summary, latency/cost, and error category. Private content remains behind the existing ownership
and retention controls.
