# ADR 0004: governed curated corpus and bounded connectors

## Context

The PRD requires a larger, refreshable corpus while preserving the evidence-first and privacy
boundaries. Unbounded crawling would create SSRF, licensing, provenance and reproducibility risks.

## Decision

Use an explicit catalog with 16 deterministic collection definitions. Every connector must provide
approved hosts and paths, and candidates are validated before network access. Store immutable
content versions with hashes and provenance; classify stale, disabled, retrying and dead-letter
states separately. Keep private content in an owner-scoped connector seam and never promote it to
the public corpus. Expose aggregate governance status through a read-only operator endpoint and
record redacted run telemetry.

## Consequences

The local portfolio slice is deterministic and auditable without live provider credentials. Adding
a source requires a catalog review and migration-safe policy record. Live scheduling, external
robots/ToS review and provider-specific credentials remain deployment concerns, but cannot bypass
the allowlist or state machine.
