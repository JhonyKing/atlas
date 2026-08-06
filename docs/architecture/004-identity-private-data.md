# Feature 004 — identity and private-data architecture

ATLAS keeps the public anonymous journey intact while adding an optional authenticated boundary.
API code depends on `AuthPort`/`SessionService`, not on a provider SDK. The local fake adapter is
deterministic; a Supabase-compatible adapter can be introduced without changing domain contracts.

## Boundaries

1. `AnonymousIdentityMiddleware` continues to issue the HMAC visitor cookie. Signing in does not
   replace that identity, so existing anonymous answer/comparison quota semantics remain stable.
2. Authenticated sessions are opaque HttpOnly cookies. The provider stores only a digest; traces
   and responses never include raw session tokens.
3. Application ownership checks return the same not-found response for missing or foreign resources.
   PostgreSQL RLS repeats this boundary using `atlas.subject_id` and `atlas.current_subject_id()`.
4. Private uploads pass filename/type/signature/size validation, quarantine and scan before parse,
   chunk, embedding or retrieval. Rejected content is never indexable.
5. Deletions use idempotency keys and a durable database job model; local tests use the same repeat-safe seam.

## Observability and privacy

Every auth/private route retains the request ID and records a redacted security event. Token,
provider-key, visitor-cookie, and private-content fields are replaced with `[REDACTED]`. LangSmith
traces may contain operation/status/ownership metadata but never raw user content.
