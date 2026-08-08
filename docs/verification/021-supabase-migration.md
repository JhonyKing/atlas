# Feature 021 verification: Supabase database migration

## Result

The project-scoped Supabase development database `fcbclsaytbjpywlaplbh` contains the exact 27
repository migration revisions, from `0001_foundation` through
`0027_revoke_public_rls_helper`.

## Checks executed

- Remote project: `AtlasAI`, active/healthy, PostgreSQL 17.6.
- Migration comparison: local 27 / remote 27, exact ordered match, no missing or unexpected
  revisions.
- Schema inventory: 47 ATLAS tables, 6 RLS-enabled tables, 8 RLS policies.
- Required functions: retrieval, quota, retention, answer-result, and provenance helpers present.
- Vector capability: pgvector installed in `extensions`; `atlas.chunk_embeddings.embedding` uses
  the vector type. Retrieval remains the repository's exact-cosine baseline, so no ANN index is
  claimed.
- SQL contracts: `001_foundation`, `003_hybrid_retrieval`, `006_provenance`,
  `008_reports`, and `010_private_data_rls` passed against the remote project.
- Security advisors: no remaining WARN findings from ATLAS functions or public helper execution;
  the remaining `public.alembic_version` RLS-without-policy result is informational and keeps the
  marker table closed.
- Performance advisors: fresh-database unindexed-FK/unused-index results are informational and
  require workload measurements before optimization.
- Data boundary: no local private rows or fixtures were copied; only repository-defined public
  seed rows are present.

## Evidence artifacts

- [Initial inspect](../../evals/results/supabase-migration-inspect-20260807-fcbclsaytbjpywlaplbh.json)
- [Apply run](../../evals/results/supabase-migration-apply-20260807-fcbclsaytbjpywlaplbh.json)
- [Final verify run](../../evals/results/supabase-migration-verify-20260807-fcbclsaytbjpywlaplbh.json)

The JSON artifacts conform to
`specs/021-supabase-database-migration/contracts/migration-evidence.schema.json` and contain no
credentials or private row payloads.
