# Implementation Plan: Optional Authentication and Private Data

**Branch**: `004-optional-auth-private-data` | **Date**: 2026-08-06 | **Spec**: [spec.md](spec.md)

## Summary

Add an optional authenticated boundary around the existing anonymous ATLAS journey. The first
vertical slice signs in a user, renews/revokes sessions, preserves anonymous quota semantics,
protects saved research/report ownership, and safely deletes user-owned data. Private uploads are
introduced only after ownership is proven and are never promoted to the public corpus automatically.

## Technical Context

**Language/Version**: Python 3.13, TypeScript/Node 24

**Primary Dependencies**: FastAPI/Pydantic, PostgreSQL/Alembic with row-level authorization,
Next.js strict TypeScript, Playwright, pytest, provider-independent AuthPort, and a
Supabase-compatible Auth/Postgres deployment adapter

**Storage**: PostgreSQL for identities, ownership and lifecycle metadata; private object storage
behind a quarantine adapter; public corpus remains separate

**Testing**: pytest, OpenAPI contract tests, SQL policy tests, Playwright, deterministic eval cases,
lint/type checks, and a redaction/security regression suite

**Target Platform**: local Docker and the existing CI deployment target

**Project Type**: modular web application with FastAPI API/workers and Next.js web client

**Performance Goals**: session endpoints remain within the existing API latency budget; upload
validation is bounded by file-size and timeout limits; deletion is durable and repeat-safe

**Constraints**: no secrets, raw session tokens, visitor identifiers, or private content in logs,
prompts, traces, or client bundles; anonymous quota behavior cannot regress; private files must pass
ownership, allowlist, signature, scan, and parse gates before indexing

**Scale/Scope**: one authenticated user boundary, three independently testable stories, and a
provider-neutral seam rather than a multi-provider identity platform

## Constitution Check

- Evidence Over Fluency: PASS — contract, security, browser, and deterministic evaluation evidence is required.
- Spec Before Code: PASS — `spec.md` defines three prioritized stories and measurable FR/SC identifiers.
- Test and Evaluate First: PASS — tests/evals precede implementation tasks in every story.
- Explicit Contracts and Type Safety: PASS — OpenAPI contract, typed AuthPort, Pydantic validation, and strict TypeScript are required.
- Provider Independence: PASS — identity is behind AuthPort; Supabase is a deployment adapter, not a domain dependency.
- Security and Privacy by Design: PASS — RLS, quarantine, redaction, retention, and repeat-safe deletion are explicit.
- Observable and Cost-Aware: PASS — request IDs and redacted ownership/lifecycle events are required.
- Small Vertical Slices: PASS — US1 is the MVP; US2 and US3 add independently testable boundaries.
- English-Canonical Engineering: PASS — code, identifiers, contracts, ADRs, and tests stay English; UI copy is bilingual.

## Research Summary

1. Use a narrow `AuthPort` with a deterministic local fake and a Supabase-compatible production adapter.
2. Keep the anonymous HMAC visitor identity and quota unchanged; never merge anonymous data automatically.
3. Enforce ownership twice: application guards for clear responses and database RLS for defense in depth.
4. Quarantine private uploads before scanning, parsing, chunking, embedding, or retrieval.
5. Use durable deletion jobs with idempotency keys; audit metadata is redacted and contains no private payload.

## Data Model and Contracts

- Entities are defined in [data-model.md](data-model.md): User, Session, OwnershipGrant, PrivateUpload, and DeletionJob.
- The versioned API boundary is [contracts/auth-private-data.yaml](contracts/auth-private-data.yaml).
- The executable journeys and expected evidence are [quickstart.md](quickstart.md).

## Project Structure

```text
apps/backend/src/atlas/auth/          # AuthPort, sessions, identity models
apps/backend/src/atlas/privacy/       # ownership, deletion, redaction
apps/backend/src/atlas/uploads/       # validation, quarantine, safe ingestion
apps/backend/src/atlas/api/routes/    # auth and private-data endpoints
apps/backend/tests/contract/auth/     # OpenAPI contract tests
apps/backend/tests/integration/       # auth, ownership, upload journeys
apps/backend/tests/security/          # cross-user and redaction regressions
apps/web/src/features/auth/           # session UI and localization
apps/web/src/features/private-data/   # private history and uploads UI
database/migrations/versions/         # identity, private-data and RLS migrations
database/tests/                       # SQL isolation and quarantine tests
docs/architecture/                    # implemented boundary documentation
docs/adr/                             # durable architectural decisions
```

## Implementation Sequence

1. Create paths, configuration, fixtures, typed ports, redaction, migrations, RLS, and observability primitives.
2. Write failing US1 contract/integration/browser tests, then implement sign-in, renewal, logout, and anonymous quota preservation.
3. Write failing US2 contract/API/database/browser tests, then implement ownership guards, private resource listing, and deletion.
4. Write failing US3 upload contract/security/database/browser tests, then implement quarantine, scanning gates, indexing, and cleanup.
5. Run the full quickstart and evidence suites; update README, architecture note, ADR, and verification record before convergence.

## Complexity Tracking

| Decision | Simpler alternative rejected | Reason and review condition |
|---|---|---|
| AuthPort plus provider adapter | Call a provider SDK directly from routes | Direct SDK calls leak provider types and make local tests/non-Supabase deployment brittle; revisit if a single provider becomes a documented hard dependency. |
| API guards plus database RLS | API-only ownership checks | API-only checks fail open if a future query path is missed; remove only after a measured, equivalent database authorization boundary exists. |
| Quarantine upload stage | Parse/index immediately after upload | Unsafe or private content could become searchable; revisit only when storage scanning is proven equivalent. |
| Durable deletion job | Synchronous best-effort deletes | Multi-resource deletion needs retry and idempotency; revisit after measured deletion latency and failure evidence. |
