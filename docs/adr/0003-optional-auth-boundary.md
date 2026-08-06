# ADR 0003: optional authentication and private-data boundary

## Status

Accepted for Feature 004.

## Decision

Use a provider-neutral `AuthPort` and `SessionService`, preserve the existing anonymous HMAC quota
identity, enforce ownership both in application guards and PostgreSQL RLS, quarantine uploads before
indexing, and process deletion through repeat-safe idempotency keys.

## Alternatives rejected

- Direct provider SDK calls in routes would leak provider types and make deterministic local tests harder.
- API-only authorization would fail open if a future query path missed a guard.
- Immediate parsing/indexing would allow unsafe or private content to become searchable.
- Best-effort synchronous deletion would not provide retryable account/resource cleanup.

## Consequences

The first slice has more explicit metadata and migration work, but it provides a defensible privacy
boundary for a portfolio project and leaves provider/storage seams replaceable.
