# ADR 0005: explicit orchestration and human publication gate

## Context

The PRD requires an agent graph, durable checkpoints, resumable jobs, and human review without
turning external content or model output into autonomous authority.

## Decision

Use a typed `AtlasState` and deterministic classifier/planner before any provider-backed node. Record
named routes and content-free node events. Persist safe checkpoint summaries by thread and replay key;
resume claims are single-use. Require an authorized, unexpired approve/edit decision before a
consequential answer/report can be published.

## Consequences

Runs are inspectable and reproducible in local fixtures, and failures fail closed. The first slice
does not choose providers or perform autonomous tool actions; those remain behind existing ports and
future routing work.
