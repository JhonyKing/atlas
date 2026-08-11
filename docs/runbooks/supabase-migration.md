# Supabase migration runbook

This runbook covers Feature 021 (`021-supabase-database-migration`). It migrates the
versioned ATLAS PostgreSQL schema to the project-scoped Supabase project
`fcbclsaytbjpywlaplbh`. It does not copy private user rows, local fixtures, or local credentials.
Development/staging remains the preferred target for future data-bearing migration tests.

## Required access

- Use the official hosted Supabase MCP with the project reference in the URL.
- Authenticate with OAuth in Codex. Never add a PAT, service-role key, database password, or
  bearer token to the repository, a prompt, a command argument, a trace, or an evidence artifact.
- Restart Codex after adding the MCP so the tools are available in the active session.
- The operator must classify the remote project before the first write. Production or unknown
  projects require explicit owner confirmation; that confirmation is recorded for the
  `agent_tool_rls` production run in
  `evals/results/supabase-migration-agent-tool-rls-20260811-applied.json`.

## Source of truth

The ordered revisions under `database/migrations/versions/` are the schema source of truth. Run
the local manifest check first:

```powershell
$env:PYTHONPATH = "$PWD/apps/backend/src"
& "$PWD/apps/backend/.venv/Scripts/python.exe" "$PWD/scripts/supabase/verify_repository_migrations.py"
```

The expected repository chain currently contains 32 revisions and ends at
`0032_foreign_key_indexes.py` (revision name `foreign_key_indexes`). Production remains at
`agent_tool_rls` with 31 revisions. The new revision adds covering indexes for the foreign keys
reported by the hosted performance advisor; it changes no row data or RLS policy and still requires
separate explicit production approval before MCP application.

## Current hosted status (2026-08-11)

- Remote migration head: `agent_tool_rls` at **31** revisions.
- Repository migration head: `foreign_key_indexes` at **32** revisions; local fresh-database and
  SQL-contract validation pass, but the revision is not yet applied remotely.
- Seven durable agent tables have **FORCE ROW LEVEL SECURITY** and exactly 14 policies: one
  `atlas_worker` `ALL` policy and one `atlas_readonly` `SELECT` policy per table.
- `anon` and `authenticated` have no grants on those seven tables. No row data was written by the
  migration.
- Supabase still reports **41 other `atlas` tables** with RLS disabled. This is a separate warning
  backlog; do not claim project-wide RLS is complete or expand this migration implicitly.
- Evidence: `evals/results/supabase-migration-agent-tool-rls-20260811-applied.json`. The earlier
  blocked run remains preserved as `...20260810.json`.

For a repeatable read-only check, export the bounded project state from the authenticated MCP as
JSON and run:

```powershell
$env:PYTHONPATH = "$PWD/apps/backend/src"
& "$PWD/apps/backend/.venv/Scripts/python.exe" "$PWD/scripts/supabase/inspect_remote.py" `
  --snapshot .\evals\fixtures\supabase-remote-snapshot.example.json `
  --run-id local-inspect
& "$PWD/apps/backend/.venv/Scripts/python.exe" "$PWD/scripts/supabase/compare_state.py" `
  --snapshot .\evals\fixtures\supabase-remote-snapshot.example.json
```

`apply_migrations.py` is dry-run by default. `--apply` requires both `--confirm` and
`--owner-confirmed`, and prints the ordered revisions for the authenticated MCP operator; the
script itself has no database credential or write transport.

## Safe lifecycle

1. **Inspect**: read the remote project metadata, migration history, extensions, functions,
   indexes, tables, policies, and bounded seed identifiers through the project-scoped MCP.
2. **Compare**: classify missing revisions and unexplained drift against the repository manifest.
3. **Approve**: stop for production/unknown classification, real existing data, unexplained drift,
   or missing privileges. Record the owner decision before any write. The explicit production
   approval for `agent_tool_rls` is now part of the applied evidence.
4. **Apply**: apply only reviewed, missing, ordered revisions. Stop at the first failed revision;
   never continue automatically after a failure.
5. **Verify**: run schema, pgvector, provenance, retrieval, RLS, and idempotent-rerun checks using
   non-production identities and synthetic records only.
6. **Evidence**: write an artifact conforming to
   `specs/021-supabase-database-migration/contracts/migration-evidence.schema.json` under
   `evals/results/`. Include identifiers, counts, statuses, elapsed times, and drift findings;
   exclude row payloads and secrets.

## Recovery and rollback

If a revision fails, preserve the failed evidence artifact and stop. Do not mark later revisions
as applied. Review the exact failing revision and use a reviewed corrective migration or a
Supabase-supported rollback procedure; do not edit migration history or delete tables manually.
Rerun inspection before attempting recovery.

## Definition of done

- Every reviewed repository revision is applied or explicitly recorded as pending approval; the
  current known difference is `foreign_key_indexes` pending after the 31-revision remote head.
- The final schema inventory has no unexplained drift.
- RLS, provenance, vector retrieval, and idempotent rerun checks pass.
- The inspect/apply/verify artifacts validate and contain no credentials or private content.
- The evidence paths are linked from `docs/verification/021-supabase-migration.md` and the Feature
  021 status entry.
