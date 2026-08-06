# Research: Optional Authentication and Private Data

## Decision 1: Provider-independent authentication boundary

Use an `AuthPort` that returns a normalized subject/session model. A Supabase-compatible Auth and
Postgres deployment is the target integration, while local tests use a deterministic fake adapter.

**Rationale**: It preserves provider independence, keeps secrets out of tests, and allows the
project to use Supabase later without leaking provider response objects into routes or domain code.

**Alternatives considered**: A custom password/session service would increase security surface and
maintenance; importing Supabase SDK objects throughout the app would make migration and testing
harder.

## Decision 2: Anonymous-to-authenticated continuity

Keep anonymous HMAC identity and quota accounting unchanged. Do not automatically merge anonymous
work. A future explicit migration flow may transfer selected records only after consent and a
repeat-safe ownership proof.

**Rationale**: Silent merging can expose work to the wrong account and can reset or double-count
quota. The existing anonymous journey remains a compatibility contract.

## Decision 3: Two-layer ownership enforcement

Every protected repository checks the authenticated subject, and PostgreSQL policies enforce the
same owner boundary for direct data access.

**Rationale**: Application checks provide clear errors; database policies protect against missed
call sites, administrative scripts, and future workers.

## Decision 4: Upload quarantine

Accept bytes only into a user-owned quarantine record. Validate size/signature/type, scan, parse,
hash, and attach retention metadata before chunks or embeddings are created.

**Rationale**: It prevents unsafe, malformed, or unowned content from reaching retrieval or the
public corpus.

## Decision 5: Repeat-safe deletion

Represent account/upload deletion as an idempotent job with an audit outcome and no raw content.

**Rationale**: Derived data spans multiple tables and storage systems; retries and partial failure
must be observable without re-exposing private material.

