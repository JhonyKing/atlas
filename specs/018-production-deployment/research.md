# Research: Production Deployment

## Decision 1: Split hosting by runtime responsibility

- **Decision**: Host the Next.js web application on Vercel; host the FastAPI API and ingestion worker as a container on a managed runtime; use Supabase as the managed PostgreSQL/pgvector/Auth/Storage target.
- **Rationale**: The web application benefits from Vercel preview/production environments, while the API and worker need long-lived request handling, scheduled work, migrations, connection pooling, and LangSmith/OpenTelemetry instrumentation. Putting the whole backend into web functions would create avoidable limits and would not match the existing worker contract.
- **Alternatives considered**:
  - Vercel for everything: initially rejected for the unbounded worker shape; superseded for the
    approved beta after adding collection-scoped Cron, durable queue idempotency, and a bounded
    one-run execution contract.
  - A single VM: rejected for the beta because it weakens preview isolation and makes web release evidence less explicit.
  - Self-hosted PostgreSQL: retained for local development/CI only; rejected for the public beta because it does not provide managed backups, auth, and operator access.

## Decision 2: Treat Supabase as an adapter, not a domain dependency

- **Decision**: Keep the existing repository, service, auth, RLS, retention, and deletion contracts. Configure Supabase through environment-specific adapters and migrations.
- **Rationale**: Feature 004 already defines Supabase-compatible private-data boundaries. The domain must remain testable against local PostgreSQL/pgvector and must not scatter Supabase SDK objects through the API.
- **Alternatives considered**:
  - Rewrite the domain around the Supabase client: rejected because it would couple tests and business rules to one provider.
  - Keep local Docker in production: rejected because the product would not be publicly durable or operable.

## Decision 3: Make migrations an explicit release gate

- **Decision**: Validate migrations on a fresh CI database, run a forward migration step against the target environment, then run readiness and smoke checks before promotion. Do not run automatic destructive down-migrations during rollback.
- **Rationale**: The database is the system of record and the current migration chain is versioned. Expand/contract compatibility and a forward-only rollback posture protect live data.
- **Alternatives considered**:
  - Apply migrations from application startup: rejected because multiple replicas can race and a failed app start hides migration evidence.
  - Automatically downgrade on rollback: rejected because down-migrations can destroy data and are difficult to make safe.

## Decision 4: Separate preview, staging, and production configuration

- **Decision**: Each environment has its own web/API origins, database target, Supabase keys, auth redirects, CORS allowlist, model-provider settings, and LangSmith project/tags.
- **Rationale**: Preview builds must be safe to review and must not leak production private data. Environment separation also makes release evidence attributable.
- **Alternatives considered**:
  - One shared database for all environments: rejected because it violates privacy and makes preview tests destructive.

## Decision 5: Preserve evidence for every release

- **Decision**: Emit a machine-readable release evidence bundle containing source/build IDs, migration head, corpus/model/locale versions, check results, smoke URLs, health results, and timestamps, plus a human-readable summary.
- **Rationale**: A portfolio deployment must be auditable. A green build without runtime evidence does not prove the deployed system works.
- **Alternatives considered**:
  - Only retain provider dashboard screenshots: rejected because screenshots are incomplete and hard to compare.

## Open operator inputs (not repository ambiguity)

- The approved beta does not require a managed container runtime. The repository contract stays
  provider-neutral so the portable worker image can be moved without domain changes if future
  volume or execution limits justify it.
- The operator must provide Vercel, Supabase, domain, model-provider, and LangSmith credentials. No secret is generated or committed by this feature.
