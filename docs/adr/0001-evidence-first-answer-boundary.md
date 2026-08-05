# ADR 0001: evidence-first answer boundary

- Status: accepted
- Date: 2026-08-04

## Decision

ATLAS will expose only claims that the deterministic verifier can connect to retrieved evidence in
the same answer run. Source excerpts are marked untrusted in the provider prompt, and the answer
model receives no source-selection or action tools.

## Context

The portfolio must demonstrate agentic orchestration without allowing a source document to change
system behavior. A prose-only citation instruction is not a sufficient security boundary.

## Consequences

The graph has explicit retrieval, generation, verification, and abstention stages. This adds
latency and can produce a partial/abstained answer, but it makes unsupported claims observable and
testable. Prompt-injection fixtures and Playwright safe-failure journeys are part of the release
gate.
