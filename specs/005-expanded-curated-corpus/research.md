# Research Notes: Expanded Curated Corpus

## Decision 1: Keep public collections stable

The existing `CollectionSlug` enum drives answer/comparison behavior and currently contains the
five public collections. Feature 005 uses a separate governed catalog vocabulary so adding source
families cannot silently change comparison validation or snapshot counts.

## Decision 2: Treat connectors as policy-bound adapters

Each connector receives a collection definition with approved hosts/paths and a policy review. It
returns typed candidates only; raw provider payloads are never passed to retrieval or API clients.
`SafeFetcher` remains the final HTTPS, redirect, size, content-type, and SSRF boundary.

## Decision 3: Preserve immutable source history

A source record points at one current version while every captured content hash is retained as an
immutable version. A changed hash creates a child version; unchanged content produces an explicit
unchanged outcome. Failed runs retain the last good version.

## Decision 4: Governance is a state machine

Enablement requires robots, terms, license, and human approval. Disablement, correction, and takedown
are atomic state transitions that exclude future retrieval while retaining content-free audit data.

## Decision 5: Deterministic operational evidence

Fixtures model unchanged, changed, failed, retried, dead-letter, stale, disabled, and corrected
sources. The seven-day target is tested with a controllable clock rather than waiting in real time.
