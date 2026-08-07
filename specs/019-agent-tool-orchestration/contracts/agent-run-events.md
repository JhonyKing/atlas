# Agent Run Events Contract v1

Events use a stable envelope:

```json
{
  "run_id": "uuid",
  "sequence": 12,
  "event_type": "tool_call.started",
  "occurred_at": "2026-08-07T00:00:00Z",
  "correlation_id": "uuid",
  "tool_id": "cited_answer",
  "tool_version": "1.0.0",
  "status": "running",
  "evidence_ids": [],
  "artifact_ids": [],
  "error_category": null,
  "trace_id": "string"
}
```

Allowed event types: `run.accepted`, `plan.created`, `approval.requested`, `approval.decided`,
`tool_call.started`, `tool_call.completed`, `tool_call.abstained`, `tool_call.failed`,
`verification.completed`, `run.completed`, `run.abstained`, `run.cancelled`, `run.failed`, and
`run.resumed`.

Raw provider responses, secrets, session tokens, private document bodies, and unbounded model text
are forbidden in the envelope.
