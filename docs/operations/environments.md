# ATLAS deployment environments

This file records non-secret environment identifiers after the owner provisions them. Never add
tokens, database passwords, Supabase service-role keys, or LangSmith API keys here.

| Environment | Vercel project ID | Web origin | Supabase project ref | API image digest | Status |
|---|---|---|---|---|---|
| Development | n/a | `http://localhost:8000` | Local Docker PostgreSQL | n/a | Local development only |
| Preview | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | [`atlasai-35ucmz40i-jhonykings-projects.vercel.app`](https://atlasai-35ucmz40i-jhonykings-projects.vercel.app) | `TODO_ISOLATED_TARGET` | n/a | Integration-branch web deployment `dpl_BdNauARdjjeJroNFuQ75GfiNzmEz` is `READY`; managed API/database isolation remains open |
| Staging | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Not provisioned |
| Production | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | [`https://atlasai-lilac.vercel.app`](https://atlasai-lilac.vercel.app) | `fcbclsaytbjpywlaplbh` | `TODO_MANAGED_API` | Web deployment `dpl_GtVWDMyubQKuuKi2M3mNsKRiRr4T` from `main` is `READY`; Supabase is `ACTIVE_HEALTHY`; full product remains unavailable until the managed API/worker and environment variables exist |

The Supabase project `fcbclsaytbjpywlaplbh` was explicitly identified by the owner as **main / PRODUCTION**;
it is not a development target. Read-only inspection on 2026-08-11 found Postgres `17.6`, migration
head `0028_agent_tool_orchestration`, 31 hosted Supabase migration records, and installed `vector`,
`pgmq`, `pgcrypto`, and `pg_stat_statements`. Preview and staging data isolation are still open because
Supabase branches require a paid plan and no unapproved cost was incurred. The Vercel project identifier is non-secret. The owner has already
configured and visually confirmed `apps/web` as the Root Directory in Project Settings; that action
is not pending. Vercel nevertheless installed the whole pnpm workspace and evaluated the repository
root for Git deployment `dpl_GpEevej8ekvyiJKTPcjmM8VBr92K`, while the project API reported
`framework: null` and the dashboard warned that the effective deployment configuration differed
from current Project Settings. The repository therefore also provides an equivalent monorepo build:
the root declares the same Next.js version as `apps/web`, builds `@atlas/web`, and emits
`apps/web/.next`. A managed API origin is still required before the complete product can be declared
ready.

The Git-connected deployment for commit `1bf85aa` was checked on 2026-08-11. Its complete build log
shows a successful frozen-lockfile workspace install followed by `NEXT_NO_VERSION`; this is evidence
of framework/package detection at the repository root, not evidence that the owner failed to set
the Root Directory in the dashboard. Commit `cd94bde` added the equivalent monorepo declaration at
the root. Vercel deployment `dpl_CmQzV1FW1xzQc73DoHF611cb2Azy` then detected Next.js `16.2.12`, ran
`corepack pnpm --filter @atlas/web build`, and reached `READY`. This closes the Git-connected web
build defect only; it does not by itself close the production release feature.

An MCP file-upload preview was verified on 2026-08-10 at
[`https://atlasai-hu543gtvg-jhonykings-projects.vercel.app`](https://atlasai-hu543gtvg-jhonykings-projects.vercel.app).
The UTF-8-preserving deployment evidence is recorded in
[`evals/results/vercel-preview-20260810-fixed-utf8.json`](../../evals/results/vercel-preview-20260810-fixed-utf8.json).
The earlier deployment remains historical evidence in
[`evals/results/vercel-preview-20260810.json`](../../evals/results/vercel-preview-20260810.json)
and is not overwritten. Neither direct preview is a replacement for the Git-connected
preview/production workflow.

## Production web activation — 2026-08-11

Commit `251b10c163fdd9db44ae038c8ee401d1b09932ee` was built as preview
`dpl_6NpyWJguTToL3NvWzirJWArkp9HF` and promoted to production as
`dpl_8KpDGAy7wZSjeEyXEefnPWuH3JZi`. The public HTTPS domain is
[`https://atlasai-lilac.vercel.app`](https://atlasai-lilac.vercel.app). Main then advanced to
`d596fc39415b1abaa4b47e0b2dd5b5e620a09617`; deployment
`dpl_Fn5qg6qNS9m88kWpu6Q2x6fP5481` is `READY` and contains the explicit locale-route and SVG flag
fixes. The public web is real; `NEXT_PUBLIC_API_ORIGIN` is not configured yet, so this is not a claim
that answer, comparison, report, corpus, news, auth, or agent operations work in production.

Production later advanced to commit `174150ba53db8a98603fcc49e4262424f908a505` in deployment
`dpl_GtVWDMyubQKuuKi2M3mNsKRiRr4T`. The GitHub CI run
[`31466909123`](https://github.com/JhonyKing/atlas/actions/runs/31466909123) completed successfully.
Two hosted Playwright journeys passed against the public domain: explicit Spanish/English routes,
both SVG flags, all public feature routes, professional unavailable states, and zero calls to a
localhost fallback. Four API-dependent journeys remain intentionally unexecuted until T032-T033
provide the managed API origin and its secrets.
