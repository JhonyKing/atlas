# ATLAS agent instructions

## Supabase MCP policy

- Use the official hosted Supabase MCP server only with a project-scoped URL:
  `https://mcp.supabase.com/mcp?project_ref=<PROJECT_REF>&features=database,debugging,development,docs`.
- Keep the server writable for authorized development tasks; do not add
  `read_only=true` unless the task explicitly requires a read-only audit.
- Authenticate with Codex's OAuth flow. Never put a Supabase PAT, service-role
  key, database password, or any other credential in this repository, a commit,
  or a command argument.
- Before the first write, identify the project environment (development,
  staging, or production). Do not write to production or real user data without
  explicit owner confirmation.
- Treat `database/migrations/versions/` as the intended schema state. Permanent
  changes must be represented by a reviewed, versioned migration before they
  are applied through MCP. After applying one, inspect the live schema and run
  the relevant database and application tests.
- Use MCP for safe inspection first. Do not create throw-away tables or mutate
  data merely to prove that write access exists.
- Compare the migration history in this repository with the live Supabase
  migration/schema state and record any drift before changing the database.
- Preserve RLS and ownership boundaries for private data. Never bypass them by
  switching to a service-role credential in application code.

