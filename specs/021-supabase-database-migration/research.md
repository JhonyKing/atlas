# Research: Supabase Database Migration

## Decision 1: Use the official hosted Supabase MCP

- **Decision**: Configure `https://mcp.supabase.com/mcp` with `project_ref=fcbclsaytbjpywlaplbh` and feature groups `database,debugging,development,docs`, authenticated with OAuth.
- **Rationale**: The hosted server supports project scoping and exposes database inspection/migration tools without putting a PAT or service-role key in the repository.
- **Alternatives considered**: A global account-scoped MCP was rejected because it exposes unrelated projects; direct database credentials were rejected because they create a secret-management and logging risk.
- **Reference**: [Supabase MCP Server](https://supabase.com/docs/guides/ai-tools/mcp)

## Decision 2: Treat repository migrations as intended state

- **Decision**: Use the 24 files under `database/migrations/versions/` and the SQL functions/tests under `database/` as the expected schema contract.
- **Rationale**: They are already versioned, reviewed, and used by CI. The remote project is compared against them before a write.
- **Alternatives considered**: Starting from an ad-hoc dashboard export was rejected because it would hide provenance and make drift difficult to review.

## Decision 3: Separate schema migration from data transfer

- **Decision**: First migrate schema, functions, extensions, policies, and approved public seed records. Do not copy private/user rows by default.
- **Rationale**: Schema is reproducible; private data requires an independent scope, retention decision, and owner approval.
- **Alternatives considered**: A full local dump was rejected for the first pass because the local database may contain fixtures, credentials, or private content.

## Decision 4: Gate writes by environment

- **Decision**: Inspect project metadata and representative row ownership before the first write. Stop if the project is production or contains real user data without explicit confirmation.
- **Rationale**: The MCP documentation warns that the hosted server is intended for development/testing and remote writes are consequential.
- **Alternatives considered**: Assuming the project is development because the repository is local was rejected; environment must be verified from the remote project.
