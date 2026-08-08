# Supabase migration runbook

This runbook covers Feature 021 (`021-supabase-database-migration`). It migrates the
versioned ATLAS PostgreSQL schema to the project-scoped Supabase development project
`fcbclsaytbjpywlaplbh`. It does not copy private user rows, local fixtures, or local credentials.

## Required access

- Use the official hosted Supabase MCP with the project reference in the URL.
- Authenticate with OAuth in Codex. Never add a PAT, service-role key, database password, or
  bearer token to the repository, a prompt, a command argument, a trace, or an evidence artifact.
- Restart Codex after adding the MCP so the tools are available in the active session.
- The operator must confirm that the remote project is development or staging before the first
  write. Production or unknown projects are blocked.

## Source of truth

The ordered revisions under `database/migrations/versions/` are the schema source of truth. Run
the local manifest check first:

```powershell
$env:PYTHONPATH = "$PWD/apps/backend/src"
& "$PWD/apps/backend/.venv/Scripts/python.exe" "$PWD/scripts/supabase/verify_repository_migrations.py"
```

The expected chain currently contains 27 revisions and ends at
`0027_revoke_public_rls_helper`.

## Safe lifecycle

1. **Inspect**: read the remote project metadata, migration history, extensions, functions,
   indexes, tables, policies, and bounded seed identifiers through the project-scoped MCP.
2. **Compare**: classify missing revisions and unexplained drift against the repository manifest.
3. **Approve**: stop for production/unknown classification, real existing data, unexplained drift,
   or missing privileges. Record the owner decision before any write.
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

- All 27 revisions are applied or explicitly recorded as already present.
- The final schema inventory has no unexplained drift.
- RLS, provenance, vector retrieval, and idempotent rerun checks pass.
- The inspect/apply/verify artifacts validate and contain no credentials or private content.
- The evidence paths are linked from `docs/verification/021-supabase-migration.md` and the Feature
  021 status entry.
