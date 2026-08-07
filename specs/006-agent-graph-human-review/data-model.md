# Data Model: Feature 006

## AtlasState

`thread_id`, `request_id`, `user_id`, language, intent, depth, risk, freshness, `RoutePlan`, bounded
evidence/citation references, answer/report references, quality, errors, node history, state version,
corpus/prompt/model versions, checkpoint ID, and review status.

## Checkpoint

`id`, `thread_id`, state version, completed node, replay key, redacted state hash, serialized safe
summary, created/expired timestamps, and status (`active`, `resumed`, `expired`, `corrupt`).

## ReviewRequest and ReviewDecision

Review request references a run and proposed artifact, evidence IDs, reason, required role, expiry,
and status. A decision records reviewer, action (`approve`, `edit`, `reject`), validated edit hash,
decision key, timestamp, and resulting publication state.

## NodeEvent

Request/run/thread IDs, node, route, start/end, latency, outcome, safe error code, and version tags;
no prompts, source bodies, private text, or credentials.
