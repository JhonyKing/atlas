# ATLAS deployment environments

This file records non-secret environment identifiers after the owner provisions them. Never add
tokens, database passwords, Supabase service-role keys, or LangSmith API keys here.

| Environment | Vercel project ID | Web origin | Supabase project ref | API image digest | Status |
|---|---|---|---|---|---|
| Development | n/a | `http://localhost:8000` | Local Docker PostgreSQL | n/a | Local development only |
| Preview | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | [`atlasai-35ucmz40i-jhonykings-projects.vercel.app`](https://atlasai-35ucmz40i-jhonykings-projects.vercel.app) | `TODO_ISOLATED_TARGET` | n/a | Integration-branch web deployment `dpl_BdNauARdjjeJroNFuQ75GfiNzmEz` is `READY`; managed API/database isolation remains open |
| Staging | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Not provisioned |
| Production | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | [`https://atlasai-lilac.vercel.app`](https://atlasai-lilac.vercel.app) | `fcbclsaytbjpywlaplbh` | Interim Vercel Function `prj_bhfat0NPE7QR0QViesuWM6KSmntN` | Web and owner-approved cited-answer API beta are `READY`; Supabase is `ACTIVE_HEALTHY`; scheduled ingestion Cron and full production DoD remain open |

The Supabase project `fcbclsaytbjpywlaplbh` was explicitly identified by the owner as **main / PRODUCTION**;
it is not a development target. Post-apply inspection on 2026-08-11 found Postgres `17.6`, migration
head `comparison_pricing_contract`, 33 hosted Supabase migration records, and installed `vector`,
`pgmq`, `pgcrypto`, and `pg_stat_statements`. Preview and staging data isolation are still open because
Supabase branches require a paid plan and no unapproved cost was incurred. The Vercel project identifier is non-secret. The owner has already
configured and visually confirmed `apps/web` as the Root Directory in Project Settings; that action
is not pending. Vercel nevertheless installed the whole pnpm workspace and evaluated the repository
root for Git deployment `dpl_GpEevej8ekvyiJKTPcjmM8VBr92K`, while the project API reported
`framework: null` and the dashboard warned that the effective deployment configuration differed
from current Project Settings. The repository therefore also provides an equivalent monorepo build:
the root declares the same Next.js version as `apps/web`, builds `@atlas/web`, and emits
`apps/web/.next`. An interim API origin is now available at `https://atlasai-api.vercel.app` for the
owner-approved cited-answer beta; the complete product still requires production Cron activation and its evidence bundle.

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
fixes. The public web is real and the production build now receives `NEXT_PUBLIC_API_ORIGIN` pointing
to the owner-approved Vercel API beta. The cited-answer smoke is recorded separately; comparison,
report, corpus, news, auth, and continuous agent-worker operations are not claimed by this interim
activation.

Production later advanced to commit `174150ba53db8a98603fcc49e4262424f908a505` in deployment
`dpl_GtVWDMyubQKuuKi2M3mNsKRiRr4T`. The GitHub CI run
[`31466909123`](https://github.com/JhonyKing/atlas/actions/runs/31466909123) completed successfully.
Two hosted Playwright journeys passed against the public domain: explicit Spanish/English routes,
both SVG flags, all public feature routes, professional unavailable states, and zero calls to a
localhost fallback. Four API-dependent journeys remain intentionally unexecuted until T032-T033
provide the managed API origin and its secrets.

## Public production aliases — 2026-08-11

The owner explicitly authorized changing Vercel Authentication from Standard Protection
(`all_except_custom_domains`) to preview-only protection (`preview`). This keeps preview
deployments behind Vercel login while making every generated production domain publicly
reachable. Production deployment `dpl_7xwapJ9TPjxp18riUnLsX2HSWYuZ` is `READY`.

Anonymous checks returned 200 with ATLAS content and no `noindex` directive for the primary
domain, the generated project domain used on LinkedIn, and the `main` branch production alias.
The newest inspected preview returned 302 to Vercel Authentication, confirming that preview
protection remains active. The redacted evidence is retained in
[`evals/results/vercel-production-access-20260811.json`](../../evals/results/vercel-production-access-20260811.json).

## Interim Vercel API beta activation — 2026-08-11

The owner-approved API project `prj_bhfat0NPE7QR0QViesuWM6KSmntN` is connected to
`JhonyKing/atlas`, rooted at `apps/backend`, and serves the public alias
[`https://atlasai-api.vercel.app`](https://atlasai-api.vercel.app). Production `/healthz` and
`/readyz` returned HTTP 200 with Supabase, migration, model-provider, and observability checks
ready. The web production project has `NEXT_PUBLIC_API_ORIGIN` configured to that alias and was
redeployed; the value is present in the client bundle and CORS permits the canonical web origin.

An `es-MX` cited-answer request returned HTTP 200 as an event stream with retrieval and
`answer.completed` events plus citations. Redacted, reproducible evidence is retained in
[`evals/results/vercel-api-beta-smoke-20260811.json`](../../evals/results/vercel-api-beta-smoke-20260811.json).
This is an interim HTTP beta only: T032's hosted Cron activation, restore, rollback, and complete
production Definition of Done remain open. The portable `atlas-worker` remains available for a
future higher-volume runtime, but an always-on worker is not part of the approved beta architecture.
