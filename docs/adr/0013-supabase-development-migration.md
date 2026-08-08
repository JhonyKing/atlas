# ADR 0013: Supabase as the development database target

## Status

Accepted for the development migration slice.

## Context

ATLAS uses PostgreSQL as its system of record and already has an ordered Alembic history. The
local Docker database is useful for deterministic tests, but a portfolio deployment needs a
managed development target with pgvector, RLS, migration history, and observable operations.

## Decision

Use the project-scoped Supabase MCP for the development project
`fcbclsaytbjpywlaplbh`. Keep the repository's Alembic revisions as the schema source of truth and
use OAuth-scoped MCP calls for inspect/apply/verify. Do not copy private/user rows or local
fixtures as part of schema migration. Keep the application behind PostgreSQL contracts rather
than introducing Supabase-specific persistence code.

The migration includes hosted-Supabase hardening revisions that move pgvector to `extensions`,
set an explicit search path on ATLAS functions, and remove public execution of the hosted
`rls_auto_enable()` helper.

## Consequences

- Local Docker PostgreSQL remains the reproducible test database.
- Supabase development state is auditable through 27 ordered repository revisions and non-secret
  evidence artifacts.
- Production deployment, private-data transfer, backups, and rollback remain separate approvals.
- The Supabase advisor may report informational findings for the private Alembic marker table and
  fresh-database unused indexes; these are recorded rather than hidden.

## Rejected alternatives

- Direct database passwords or service-role keys: rejected because they weaken secret handling.
- A global account-scoped MCP: rejected because it exposes unrelated projects.
- Copying a local dump: rejected because it can transfer fixtures or private content without an
  explicit data-migration decision.
