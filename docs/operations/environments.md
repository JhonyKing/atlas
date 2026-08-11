# ATLAS deployment environments

This file records non-secret environment identifiers after the owner provisions them. Never add
tokens, database passwords, Supabase service-role keys, or LangSmith API keys here.

| Environment | Vercel project ID | API origin | Supabase project ref | API image digest | Status |
|---|---|---|---|---|---|
| Development | n/a | `http://localhost:8000` | `fcbclsaytbjpywlaplbh` | n/a | Active Supabase development target; not production |
| Preview | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | [`atlasai-c2so92mef-jhonykings-projects.vercel.app`](https://atlasai-c2so92mef-jhonykings-projects.vercel.app) | `TODO_OWNER` | n/a | Git-connected web deployment `dpl_CmQzV1FW1xzQc73DoHF611cb2Azy` is `READY`; managed API/database configuration remains open |
| Staging | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Not provisioned |
| Production | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Vercel project exists; production is not declared ready because the managed API origin, environment-scoped configuration and main-branch release evidence remain open |

The development row is included only to make the current database target explicit; it must not be
used as a production identifier. The Vercel project identifier is non-secret. The owner has already
configured and visually confirmed `apps/web` as the Root Directory in Project Settings; that action
is not pending. Vercel nevertheless installed the whole pnpm workspace and evaluated the repository
root for Git deployment `dpl_GpEevej8ekvyiJKTPcjmM8VBr92K`, while the project API reported
`framework: null` and the dashboard warned that the effective deployment configuration differed
from current Project Settings. The repository therefore also provides an equivalent monorepo build:
the root declares the same Next.js version as `apps/web`, builds `@atlas/web`, and emits
`apps/web/.next`. A managed API origin and a successful Git-connected deployment are still required
before production can be declared ready.

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
