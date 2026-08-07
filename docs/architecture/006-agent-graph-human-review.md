# Feature 006 — explicit agent orchestration architecture

ATLAS now has a deterministic orchestration boundary in front of provider-backed work. The
classifier assigns intent, depth, language, risk, and freshness; the planner produces bounded
subquestions and source/date criteria; the orchestrator records an explicit terminal route
(`answer`, `comparison`, `report`, or `abstain`). Unsafe and cancelled requests stop before
retrieval or publication.

`AtlasState` is a typed, versioned envelope. It carries identifiers, route plan, evidence/citation
references, node history, node events, and version metadata. Checkpoints persist only a safe summary
and hash, keyed by `(thread_id, replay_key)`. Integrity checks, expiry, and a single-use resume
claim prevent corrupted or duplicated replay. PostgreSQL migration `0024_agent_checkpoints_reviews`
stores the durable checkpoint and review tables with restricted grants.

Human review is a separate state machine. A reviewer can approve, edit, or reject a proposal; only
approved or validated-edited requests are publishable. Decisions are authorization-checked,
expiry-aware and repeat-safe. The API exposes planning, review, thread status, and resume while
excluding request bodies and private state from responses.
