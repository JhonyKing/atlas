# ADR 0002: Evidence-backed report boundary

## Status

Accepted for Feature 003's first vertical slice.

## Decision

Reports are generated only from a completed, visitor-visible comparison run. A provider or
renderer may localize presentation text, but it may not create new evidence IDs, replace source
excerpts, or mark a citation-less factual section complete. DOCX and PDF are rendered from one
neutral structured representation and are validated before publication.

## Rationale

This preserves the project's evidence-first constitution and prevents format-specific or
language-specific citation drift. Separating metadata from binary files also provides a clean seam
for expiry, ownership, idempotency, reproducibility, and a future managed object store.

## Consequences

- The comparison run must expose evidence identities before a report can complete.
- The first implementation is intentionally in-process and local; worker and object-store scale
  are deferred until measured demand requires them.
- Spanish is a presentation locale. Original evidence remains labelled and traceable.

