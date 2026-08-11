# Feature 019 SpecKit convergence - 2026-08-10

Convergence was run from branch `codex/019-agent-tool-orchestration` after the durable replay,
actor ownership, consent, daily-news evidence, and idempotency slices.

## Scope checked

- `spec.md`: 16 functional requirements, buildable success criteria, four user stories, and edge
  cases.
- `plan.md`: adapter boundaries, PostgreSQL persistence, checkpoint/replay, observability, and
  deployment constraints.
- `tasks.md`: 49 task IDs across nine phases, including the previous convergence tasks.
- Constitution: all nine principles, with the RLS exposure treated as a security MUST violation.

## Findings

| Finding | Severity | Evidence | Remaining task |
|---|---|---|---|
| Durable run persistence still needs complete cross-process replay integration beyond the per-tool checkpoint/resume contract. | HIGH | `apps/backend/src/atlas/api/routes/agent.py`, `apps/backend/src/atlas/agent/checkpoints.py` | T021 |
| Production LangSmith/evidence traces and useful-progress latency are not recorded for all required run outcomes. | HIGH | `evals/results/`, `docs/verification/019-agent-tool-orchestration.md` | T033, T046 |
| Read-only route results still need durable provenance/excerpt/relation envelopes for every domain adapter. | HIGH | `apps/backend/src/atlas/api/routes/agent.py`, `apps/backend/src/atlas/agent/tools/read_only.py` | T045 |
| Full policy convergence still needs agent-specific quota and scope enforcement in addition to approval, consent, target, owner, and idempotency checks. | HIGH | `apps/backend/src/atlas/agent/policy.py`, `apps/backend/src/atlas/api/routes/agent.py` | T043 |
| PostgreSQL event ordering and durable actor ownership are implemented and covered by focused tests. | INFO | `apps/backend/src/atlas/persistence/agent_runs.py` | T047/T048 are implemented; follow-up integration evidence remains in T038. |
| RLS policy migration is present in the repository but not applied to Supabase because the MCP rejected the unapproved `FORCE RLS` blast radius. | CRITICAL | `database/migrations/versions/0031_agent_tool_rls.py`, `evals/results/supabase-migration-agent-tool-rls-20260810.json` | T049 |

## Outcome

Convergence is **not clean**. No existing task was deleted or renumbered. The findings are already
represented by open tasks T021, T033, T038, T040, T043, T045, T046, and T049; no duplicate convergence tasks
were added. Feature 019 remains open until the mandatory local gates, live evidence, integration
evidence, and reviewed Supabase policy deployment are complete.

## Post-convergence update (2026-08-11)

The owner approved the reviewed worker/read-only policy design and the Supabase MCP applied
`agent_tool_rls` in production. T049 is now complete with post-apply evidence in
`evals/results/supabase-migration-agent-tool-rls-20260811-applied.json`. The historical blocked
finding above is preserved as evidence of the pre-approval state. Supabase still reports 41
other `atlas` tables without RLS; that project-wide backlog is intentionally separate from T049.

The durable persistence finding is now resolved by the cross-repository run/event replay contract
(`apps/backend/tests/agent/test_postgres_agent_persistence.py`, 12 tests passed). T021 is marked
complete; the remaining Feature 019 gaps are policy convergence, complete read-only result
envelopes, and the full browser/deployment gate.
