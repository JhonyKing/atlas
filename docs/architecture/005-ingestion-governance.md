# Feature 005 — ingestion governance architecture

The ingestion boundary is deliberately separate from answer retrieval. A catalog entry owns an
explicit HTTPS host/path allowlist, refresh interval, TTL and policy state. Discovery produces
candidates; `InMemoryGovernanceRepository.plan_discovery` rejects anything outside that allowlist
before a fetcher can run. Production fetching continues to use `SafeFetcher`, which adds DNS-level
SSRF and redirect checks.

Each accepted capture stores provenance and a content hash. A changed hash creates a new immutable
source version and supersedes the previous version; an unchanged hash is idempotent. A failed
refresh never replaces the last-good version. Policy disablement or takedown marks retrieval state
disabled while preserving audit history. Private connector records carry an owner identifier and
are never inserted into the public collection path.

The PostgreSQL migration `0022_ingestion_governance` mirrors these boundaries with separate tables,
foreign keys, immutable-version uniqueness, indexes and revoked public grants. The operator panel
reads only aggregate coverage (source counts, stale/disabled counts, retries and dead letters),
not source bodies. Run telemetry contains run ID, collection, outcome, latency and a safe error
code; it is suitable for LangSmith tags without leaking content or credentials.
