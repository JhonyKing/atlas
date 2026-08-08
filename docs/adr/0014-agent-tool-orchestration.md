# ADR 0014: versioned agent tools with explicit approval

## Context

ATLAS has several research capabilities, but exposing them as unrestricted model tools would make
private data access, deletion, publication, and evidence provenance ambiguous.

## Decision

Use a versioned allowlist of typed tools. A planner may propose a finite plan, but only the server
can validate and execute it. Read-only capabilities delegate to existing domain services. Private,
mutating, deleting, and publishing capabilities require a short-lived approval bound to actor,
tool version, target, normalized arguments, plan, and idempotency context. All runs emit an ordered,
content-safe event envelope and preserve evidence/artifact IDs.

The default planner label is GPT-5.6 Luna through the existing provider boundary. Provider output is
never treated as authorization and a provider outage fails closed or abstains.

## Consequences

- The UI can present a real tool choice, typed form, plan preview, approval card, and reconnectable
  timeline.
- New tools require a catalog version, schema, policy, adapter, tests, and documentation.
- The local repository remains an in-memory contract adapter until the production repository wiring
  is completed in the deployment feature.
