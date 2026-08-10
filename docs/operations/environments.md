# ATLAS deployment environments

This file records non-secret environment identifiers after the owner provisions them. Never add
tokens, database passwords, Supabase service-role keys, or LangSmith API keys here.

| Environment | Vercel project ID | API origin | Supabase project ref | API image digest | Status |
|---|---|---|---|---|---|
| Development | n/a | `http://localhost:8000` | `fcbclsaytbjpywlaplbh` | n/a | Active Supabase development target; not production |
| Preview | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Not provisioned |
| Staging | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Not provisioned |
| Production | `prj_uk5h2ryyeHSYfi2AgL78cUM5TNis` | `TODO_OWNER` | `TODO_OWNER` | `TODO_OWNER` | Vercel project exists, but is linked to `JhonyKing/atlasai`; Git deployment failed |

The development row is included only to make the current database target explicit; it must not be
used as a production identifier. The Vercel project identifier is non-secret, but the repository
link and deployment state remain an open operator task until the project is linked to
`JhonyKing/atlas` and a managed API origin exists.

An MCP file-upload preview was verified on 2026-08-10 at
`https://atlasai-re1bz6669-jhonykings-projects.vercel.app`. It is recorded in
[`evals/results/vercel-preview-20260810.json`](../../evals/results/vercel-preview-20260810.json)
and is not a replacement for the Git-connected preview/production workflow.
