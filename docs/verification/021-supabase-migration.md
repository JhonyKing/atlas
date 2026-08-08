# Feature 021 verification: Supabase database migration

## Result

The project-scoped Supabase development database `fcbclsaytbjpywlaplbh` contains the exact 27
repository migration revisions, from `0001_foundation` through
`0027_revoke_public_rls_helper`.

## Checks executed

- Local quality gate: database unit tests **12 passed**, Ruff passed, mypy passed for the database
  package, and the repository manifest command reported 27 revisions.
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

## Repeatable workflow evidence

The repository includes deterministic, read-only helpers that accept a bounded snapshot exported
by the project-scoped Supabase MCP:

- `scripts/supabase/inspect_remote.py` creates an inspect artifact without performing writes.
- `scripts/supabase/compare_state.py` reports exact revision/object drift and exits non-zero on it.
- `scripts/supabase/apply_migrations.py` plans only the missing ordered suffix and requires explicit
  confirmation flags before handing the plan to the MCP operator.
- `scripts/supabase/verify_security_retrieval.py` validates vector, retrieval, provenance, and RLS
  results without accepting row payloads.
- `scripts/verify-supabase-migration.ps1` is the CI wrapper. The GitHub Action in
  `.github/workflows/supabase-migration.yml` runs repository/evidence checks on pull requests;
  its optional dispatch job accepts an owner-provided snapshot for read-only comparison. No CI
  job applies migrations.

The contract and failure-path tests cover 25 checks locally, including no-op reruns, stop-on-first-
failure behavior, and a bounded verification latency assertion.

SpecKit closure: Analyze covered all 13 functional requirements and 6 buildable success criteria
without CRITICAL/HIGH findings. Converge found no remaining unbuilt work, so no convergence phase
was appended to `tasks.md`.
