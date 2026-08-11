# Feature 021 verification: Supabase database migration

## Latest owner-approved production hardening (2026-08-11)

The owner authorized the reviewed `agent_tool_rls` migration for the production project
`fcbclsaytbjpywlaplbh`. The Supabase MCP applied revision `agent_tool_rls`; the remote history now
contains **31** revisions and reports that revision as the head.

Post-apply inspection verified all seven durable agent tables (`agent_plans`, `agent_runs`,
`agent_tool_calls`, `agent_run_events`, `agent_approvals`, `agent_idempotency_records`, and
`agent_checkpoint_claims`) with **FORCE ROW LEVEL SECURITY** enabled and exactly two policies
each: an `atlas_worker` `ALL` policy and an `atlas_readonly` `SELECT` policy. `anon` and
`authenticated` have zero grants on those tables; the reviewed worker/read-only grants remain
available. The migration changed schema/policy state only and wrote no user or private rows.

This does **not** close project-wide RLS. Supabase still reports **41 other `atlas` tables** with
RLS disabled. They are a separate security backlog requiring their own reviewed policy design and
migrations. The informational `public.alembic_version` RLS-without-policy advisor finding is also
preserved without changing the marker table.

Applied-run evidence: [owner-approved agent-tool RLS verification](../../evals/results/supabase-migration-agent-tool-rls-20260811-applied.json).
The earlier blocked attempt remains preserved at
`../../evals/results/supabase-migration-agent-tool-rls-20260810.json` and was not overwritten.

## Result

The project-scoped Supabase development database `fcbclsaytbjpywlaplbh` contains the exact 28
repository migration revisions, from `0001_foundation` through
`0028_agent_tool_orchestration`. The application marker in `public.alembic_version` was found one
revision behind after the hosted MCP apply and was reconciled to
`0028_agent_tool_orchestration` on 2026-08-10. This was a development-target metadata repair; no
production target was changed.

## Checks executed

- Local quality gate: database unit tests **12 passed**, Ruff passed, mypy passed for the database
  package, and the repository manifest command reported 27 revisions.
- Remote project: `AtlasAI`, active/healthy, PostgreSQL 17.6.
- Migration comparison: local 28 / remote 28, exact ordered match, no missing or unexpected
  revisions.
- Schema inventory: 53 ATLAS tables, including the five `0028_agent_tool_orchestration` tables;
  the hosted application marker now reports the same `0028` head.
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
- Data boundary: no local private rows or fixtures were copied. Five collection seed rows are
  present, while `sources`, `source_versions`, `chunks`, `chunk_embeddings`, `news_candidates`,
  `answer_runs`, and `comparison_runs` are empty until the real ingestion/refresh workflow runs.

## Evidence artifacts

- [Initial inspect](../../evals/results/supabase-migration-inspect-20260807-fcbclsaytbjpywlaplbh.json)
- [Apply run](../../evals/results/supabase-migration-apply-20260807-fcbclsaytbjpywlaplbh.json)
- [Final verify run](../../evals/results/supabase-migration-verify-20260807-fcbclsaytbjpywlaplbh.json)
- [Marker reconciliation](../../evals/results/supabase-marker-reconcile-20260810-fcbclsaytbjpywlaplbh.json)

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
