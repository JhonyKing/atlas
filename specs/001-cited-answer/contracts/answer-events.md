# Contract: Cited Answer Event Stream

`POST /v1/answers` returns UTF-8 `text/event-stream`. The HTTP response carries
`X-Atlas-Run-ID` and `X-Request-ID`. Each SSE `id` is a monotonically increasing integer scoped to
the run; each `data` value is one JSON object. Heartbeat comments may be emitted and are not events.

## Safety rule

Progress events MUST NOT contain draft claims, excerpts, prompt content, model reasoning, or source
URLs. A complete answer and its citations appear only in `answer.completed` after the deterministic
citation gate passes. An unverified draft is never public.

## Common event envelope

```json
{
  "run_id": "0198...",
  "sequence": 1,
  "occurred_at": "2026-08-04T18:00:00Z",
  "stage": "retrieving"
}
```

Every event includes those fields plus the event-specific fields below.

## Events

### `run.accepted`

First event after quota and idempotency reservation.

```json
{
  "run_id": "0198...",
  "sequence": 1,
  "occurred_at": "2026-08-04T18:00:00Z",
  "stage": "accepted",
  "quota": {"limit": 10, "remaining": 9, "window_hours": 24},
  "corpus_snapshot_id": "0198..."
}
```

### `retrieval.started`

Signals that the validated question is being searched. No result content is exposed.

### `retrieval.completed`

```json
{
  "run_id": "0198...",
  "sequence": 3,
  "occurred_at": "2026-08-04T18:00:01Z",
  "stage": "retrieving",
  "candidate_count": 20,
  "selected_count": 8
}
```

Counts are safe to expose; IDs, scores, and excerpts remain private until final verification.

### `generation.started`

Signals structured answer composition. It contains no model identifier or draft text.

### `verification.started`

Signals claim/evidence validation. It contains no draft text.

### `answer.completed`

Terminal event. Its `result` is exactly the `AnswerResult` schema from `openapi.yaml` with status
`completed` and answer status `complete` or `partial`.

```json
{
  "run_id": "0198...",
  "sequence": 6,
  "occurred_at": "2026-08-04T18:00:04Z",
  "stage": "completed",
  "result": {"run_id": "0198...", "status": "completed", "answer_status": "complete"}
}
```

The abbreviated result above illustrates the envelope; production payloads MUST satisfy the full
OpenAPI schema.

### `answer.abstained`

Terminal event. Its `result` satisfies `AnswerResult` with status/answer status `abstained`, an
empty or supported-only claims list, and at least one human-readable limitation. It MUST NOT include
a fabricated citation.

### `run.cancelled`

Terminal event when explicit cancellation is processed before the connection closes. A direct
disconnect may prevent delivery; persisted status remains queryable while retained.

### `run.failed`

Terminal controlled error.

```json
{
  "run_id": "0198...",
  "sequence": 4,
  "occurred_at": "2026-08-04T18:00:03Z",
  "stage": "failed",
  "error": {
    "code": "MODEL_TEMPORARILY_UNAVAILABLE",
    "message": "ATLAS could not complete this answer. Please try again.",
    "retryable": true
  }
}
```

Errors contain controlled public codes and messages, never exceptions, provider bodies, prompts,
SQL, credentials, or internal URLs.

## Ordering and terminal behavior

- `run.accepted` is first.
- Each sequence number is exactly one greater than the previous delivered event.
- Retrieval precedes generation; generation precedes verification.
- Exactly one terminal event is persisted: `answer.completed`, `answer.abstained`, `run.cancelled`,
  or `run.failed`.
- No event follows a terminal event.
- Clients MUST treat disconnect as cancellation unless a terminal event was already received.
- A repeated request with the same idempotency key returns the existing run outcome and does not
  reserve quota again; it never starts two streams for the same active work.

## Accessibility-facing status text

The web application maps stages to concise live-region messages:

| Stage | Public message |
|-------|----------------|
| accepted | `Question accepted.` |
| retrieving | `Searching the verified source collection.` |
| composing | `Preparing a cited answer.` |
| verifying | `Checking every citation.` |
| completed | `Verified answer ready.` |
| abstained | `ATLAS could not verify a complete answer.` |
| failed | `ATLAS could not complete this answer.` |

Messages use an `aria-live="polite"` region. Progress and outcome are never communicated by color
alone.
