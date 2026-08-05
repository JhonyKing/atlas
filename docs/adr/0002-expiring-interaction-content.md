# ADR 0002: expire anonymous content, preserve aggregates

- Status: accepted
- Date: 2026-08-04

## Decision

Answer questions, evidence links, claims, feedback comments, and diagnostics expire after 30 days.
The retention function rolls up only controlled daily metrics, deletes content in bounded
`SKIP LOCKED` batches, and stores an ID/timestamp-only tombstone for an expired run.

## Context

ATLAS is anonymous and intended for a portfolio launch. Keeping raw questions or source excerpts
indefinitely would violate the stated privacy boundary and make deletion difficult to demonstrate.

## Consequences

The product can report aggregate quality/latency/cost trends after deletion, while an expired answer
returns a controlled retention state instead of resurrecting content. A scheduler outage can delay
purging, so the runbook verifies batch progress and retries safely.
