# Quickstart: Supabase Database Migration

This guide is intentionally read-first. Do not run a remote write until the project environment is confirmed as development/staging and the owner has approved the migration run.

## Prerequisites

- Codex session restarted after adding the Supabase MCP so the `supabase` tools are callable.
- OAuth login completed for the project-scoped MCP.
- Repository clean enough to identify the commit being migrated.
- No Supabase PAT, service-role key, database password, or private row data in commands or logs.

## 1. Inspect remote state

Use the Supabase MCP to identify the project and environment, then read:

- migration history;
- tables, extensions, indexes, functions, and RLS policies;
- pgvector availability;
- bounded row counts and seed identifiers only.

Export an `inspect` artifact conforming to `contracts/migration-evidence.schema.json`.

## 2. Compare repository state

Compare the remote inventory with:

- `database/migrations/versions/`;
- `database/functions/`;
- `database/tests/`.

Stop on unexplained drift, production classification, or missing required privileges.

## 3. Apply schema changes

Apply reviewed migrations in dependency order through MCP. Do not copy local private/test rows by default. Stop on the first failed revision and record the failure in the evidence artifact.

## 4. Verify behavior

Run the relevant SQL checks and backend integration checks against the remote development project. Confirm RLS isolation, evidence provenance, vector retrieval, idempotent rerun behavior, and function availability.

## 5. Re-run verification

Run the inspect/verify workflow a second time. Expected result: no new revisions, no duplicate objects, no unexplained drift, and a `passed` evidence artifact.
