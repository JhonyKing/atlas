# ATLAS deployment environments

This file records non-secret environment identifiers after the owner provisions them. Never add
tokens, database passwords, Supabase service-role keys, or LangSmith API keys here.

| Environment | Vercel project ID | API origin | Supabase project ref | API image digest | Status |
|---|---|---|---|---|---|
| Development | n/a | `http://localhost:8000` | `fcbclsaytbjpywlaplbh` | n/a | Active Supabase development target; not production |
| Preview | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Not provisioned |
| Staging | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Not provisioned |
| Production | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Vercel project exists; latest deployment `dpl_7RCLdYHmuEhiNUEc9uZgA6PVPoKn` failed because the configured root did not expose a Next.js package |

The development row is included only to make the current database target explicit; it must not be
used as a production identifier. The Vercel project identifier is non-secret, but the repository
root/build state and deployment remain an open operator task until the project is linked to
`JhonyKing/atlas` with `apps/web` as its Root Directory (or an equivalent monorepo build command)
and a managed API origin exists. MCP evidence from 2026-08-11 reports the exact build failure:
`No Next.js version detected. Make sure your package.json has "next" ... and Root Directory ...`.

An MCP file-upload preview was verified on 2026-08-10 at
[`https://atlasai-hu543gtvg-jhonykings-projects.vercel.app`](https://atlasai-hu543gtvg-jhonykings-projects.vercel.app).
The UTF-8-preserving deployment evidence is recorded in
[`evals/results/vercel-preview-20260810-fixed-utf8.json`](../../evals/results/vercel-preview-20260810-fixed-utf8.json).
The earlier deployment remains historical evidence in
[`evals/results/vercel-preview-20260810.json`](../../evals/results/vercel-preview-20260810.json)
and is not overwritten. Neither direct preview is a replacement for the Git-connected
preview/production workflow.
