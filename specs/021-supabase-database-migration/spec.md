# Feature Specification: Supabase Database Migration

**Feature Branch**: `021-supabase-database-migration`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Escribe todo lo que debas escribir en Supabase; hay que migrar la base de datos ahí."

## User Scenarios & Testing

### User Story 1 - Provision the ATLAS schema in Supabase (Priority: P1)

As the project owner, I want the complete ATLAS database schema available in the selected Supabase development project so the application can stop depending on the local-only PostgreSQL instance.

**Why this priority**: Without the schema, the deployed application cannot persist users, corpus evidence, answers, comparisons, reports, or agent checkpoints.

**Independent Test**: Apply the repository's versioned database changes to the selected Supabase project and verify that every expected table, function, index, extension, and migration marker exists without executing application writes.

**Acceptance Scenarios**:

1. **Given** a project-scoped Supabase connection, **When** the migration is applied, **Then** all 27 repository migration revisions are represented in the remote migration history in order.
2. **Given** the migrated schema, **When** the schema inventory is queried, **Then** all ATLAS tables, constraints, indexes, SQL functions, and required extensions are present.
3. **Given** an already migrated project, **When** the same migration verification is repeated, **Then** no duplicate objects or destructive changes are produced.

### User Story 2 - Preserve security and retrieval behavior (Priority: P1)

As the project owner, I want the Supabase schema to preserve ATLAS's private-data boundaries, evidence provenance, and vector retrieval capabilities so moving the database does not weaken product guarantees.

**Why this priority**: The application handles private uploads and evidence-backed answers; a migration that loses RLS, provenance, or vector search is unacceptable.

**Independent Test**: Inspect and execute the repository's database security and retrieval checks against the migrated project, using non-production test identities and data only.

**Acceptance Scenarios**:

1. **Given** private-data tables, **When** access is evaluated as an anonymous user, **Then** rows belonging to another user are not readable or writable.
2. **Given** evidence and answer records, **When** provenance and citation queries run, **Then** canonical URLs, capture timestamps, hashes, and evidence relationships remain available.
3. **Given** the vector retrieval capability, **When** the extension and retrieval function are checked, **Then** the required vector type, index, and search function are usable.

### User Story 3 - Establish a repeatable migration workflow (Priority: P2)

As a contributor, I want future schema changes to be authored in the repository, applied to Supabase through an authenticated project-scoped workflow, and verified with evidence so local, CI, and remote states cannot silently diverge.

**Why this priority**: A one-time migration is not enough; the portfolio project must demonstrate disciplined database operations.

**Independent Test**: Create a no-op verification run after migration, compare repository revisions with the remote migration history, and record the result without modifying data.

**Acceptance Scenarios**:

1. **Given** a new versioned migration in the repository, **When** it is reviewed, **Then** the change has an explicit rollback or safety rationale and a corresponding database test.
2. **Given** the repository and Supabase migration inventories, **When** they are compared, **Then** drift is reported with the exact revision or object that differs.
3. **Given** a failed migration, **When** the workflow stops, **Then** the failure is recorded and no later migration is applied automatically.

## Edge Cases

- The Supabase project may already contain some ATLAS objects; the workflow must detect and reconcile existing revisions instead of blindly recreating them.
- The remote project may be production or contain real user data; the workflow must stop before the first write unless the owner has explicitly confirmed that environment.
- A migration may require an extension or permission unavailable on the selected Supabase plan; the workflow must report the missing capability and leave the repository unchanged.
- The local database may contain seed or test data that must not be copied to the remote project; schema migration and data migration must be treated as separate, auditable operations.
- Network interruption or a partial migration must be recoverable through the migration history without rerunning already-applied revisions.

## Requirements

### Functional Requirements

- **FR-001**: The project MUST use the Supabase project identified by `fcbclsaytbjpywlaplbh` and no other project for this feature.
- **FR-002**: The migration MUST represent all 27 versioned revisions currently present under `database/migrations/versions/` in dependency order.
- **FR-003**: The migration MUST preserve all tables, primary keys, foreign keys, unique constraints, check constraints, indexes, SQL functions, and seed records required by the current ATLAS application.
- **FR-004**: The migration MUST enable and verify the vector-search capability required by the current retrieval function and embedding columns.
- **FR-005**: The migration MUST preserve row-level security policies and private-data ownership rules for identities, uploads, reports, comparisons, and agent checkpoints.
- **FR-006**: The migration MUST preserve evidence provenance fields and the relationships used to verify cited answers and comparison cells.
- **FR-007**: The workflow MUST inspect the remote schema and migration history before applying any write.
- **FR-008**: The workflow MUST use OAuth-authenticated, project-scoped Supabase MCP access and MUST NOT place a PAT, service-role key, database password, or other credential in source control, prompts, logs, or command arguments.
- **FR-009**: The workflow MUST apply only reviewed, versioned schema changes and MUST stop on the first failed migration.
- **FR-010**: The workflow MUST be idempotent: rerunning verification or an already-applied migration MUST NOT duplicate objects or delete data.
- **FR-011**: The workflow MUST run the relevant SQL security, retrieval, and application integration tests against the remote development project after migration.
- **FR-012**: The workflow MUST produce an evidence artifact containing the project reference, applied revisions, schema inventory, extension status, RLS checks, retrieval checks, and any drift findings without exposing secrets or private row contents.
- **FR-013**: Data transfer from the local database MUST be opt-in and separately approved from schema migration; test fixtures and local-only credentials MUST NOT be copied to Supabase by default.

### Key Entities

- **Migration revision**: An ordered, versioned schema change tracked both in the repository and by the remote project.
- **Schema inventory**: The auditable set of remote tables, constraints, indexes, functions, extensions, and policies expected by ATLAS.
- **Migration evidence artifact**: A non-secret report proving which revisions and checks completed against the selected project.
- **Environment classification**: The development, staging, or production classification that gates the first remote write.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of the 27 repository migration revisions are applied or explicitly recorded as already present in the selected Supabase project.
- **SC-002**: The remote schema inventory has zero unexplained differences from the repository's expected schema after migration.
- **SC-003**: 100% of applicable database security and retrieval checks pass against the remote development project.
- **SC-004**: A second verification run completes without creating duplicate objects, changing row counts, or applying a new revision.
- **SC-005**: The migration evidence artifact contains no API key, password, bearer token, service-role credential, or private user content.
- **SC-006**: A contributor can identify the exact repository revision, remote revision, verification result, and next action for every migration change.

## Assumptions

- The supplied project reference is a development Supabase project; if verification shows production or real user data, the first write pauses for owner confirmation.
- The repository's 27 Alembic revisions are the intended schema source of truth; no untracked remote schema is accepted without an explicit drift decision.
- The first pass migrates schema, functions, extensions, policies, and approved seed data. Bulk user/private data transfer is a separate follow-up operation.
- Supabase MCP OAuth access is available to the project owner and is scoped only to the supplied project reference.
- The application will continue to use PostgreSQL-compatible database access after the migration; provider-specific client code is out of scope for this feature.
