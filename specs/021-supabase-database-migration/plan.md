# Implementation Plan: Supabase Database Migration

**Branch**: `021-supabase-database-migration` | **Date**: 2026-08-07 | **Spec**: [spec.md](./spec.md)

## Summary

Migrate the ATLAS PostgreSQL schema and approved seed state from the repository's 27 ordered Alembic revisions into the project-scoped Supabase development project `fcbclsaytbjpywlaplbh`. The workflow will inspect the remote state first, apply only reviewed versioned changes through the authenticated Supabase MCP, verify extensions/functions/RLS/retrieval behavior, and produce a non-secret evidence artifact. Bulk private or user data is explicitly separated from schema migration.

## Technical Context

**Language/Version**: Python 3.13 runtime in `apps/backend/.venv`; SQL executed by PostgreSQL 17-compatible Supabase

**Primary Dependencies**: Alembic, SQLAlchemy, psycopg, Supabase hosted MCP with `database`, `debugging`, `development`, and `docs` feature groups

**Storage**: PostgreSQL with pgvector; Supabase project `fcbclsaytbjpywlaplbh`

**Testing**: Repository SQL checks in `database/tests/`, backend pytest integration checks, migration-history comparison, MCP schema inspection

**Target Platform**: Supabase development project; production data is out of scope until separately approved

**Project Type**: Web application with Python API, worker, and PostgreSQL system of record

**Performance Goals**: Migration verification completes with bounded queries and reports useful elapsed time; no unbounded table scans or bulk private-data reads

**Constraints**: Project-scoped OAuth only; no PAT/service-role/password in source control or commands; stop on first failed migration; preserve RLS and evidence provenance; reruns must be idempotent

**Scale/Scope**: 27 repository revisions, all current ATLAS schema objects/functions/policies/extensions, approved public seed records only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Evidence Over Fluency**: PASS — migration evidence records revisions, object inventory, RLS checks, and drift without private content.
- **Spec Before Code**: PASS — this feature has an approved specification before remote writes.
- **Test and Evaluate First**: PASS — inspect and test the remote state before applying writes; run SQL and integration checks after migration.
- **Explicit Contracts and Type Safety**: PASS — evidence output has a JSON schema; existing migration files remain the source contract.
- **Provider Independence**: PASS — application PostgreSQL contracts stay behind existing database configuration; Supabase MCP is an operations channel, not an application dependency.
- **Security and Privacy by Design**: PASS — project-scoped OAuth, environment gate, RLS verification, and no credential logging.
- **Observable and Cost-Aware**: PASS — record elapsed time, revision counts, failure stage, and drift; avoid private row capture.
- **Small Vertical Slices**: PASS — schema verification, migration, security/retrieval verification, and evidence export are independently testable.
- **English-Canonical Engineering**: PASS — code and engineering artifacts remain English.

## Phase 0: Research Decisions

See [research.md](./research.md). Key decisions are to use the official hosted Supabase MCP with project scope, treat repository migrations as intended state, keep schema and data transfer separate, and require a development-environment gate before the first write.

## Phase 1: Design

- [data-model.md](./data-model.md) defines the migration evidence and drift records.
- [contracts/migration-evidence.schema.json](./contracts/migration-evidence.schema.json) defines the non-secret evidence artifact.
- [quickstart.md](./quickstart.md) defines the read-first, apply, verify, and rerun checks.

## Project Structure

```text
database/
├── migrations/versions/       # 27 ordered Alembic revisions (source of truth)
├── functions/                 # SQL function definitions
└── tests/                     # SQL security, retrieval, and integrity checks
apps/backend/
├── src/atlas/                  # runtime database contracts and services
└── tests/                      # integration and unit checks
specs/021-supabase-database-migration/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/migration-evidence.schema.json
└── tasks.md
docs/operations/
└── supabase-migration.md      # durable operator runbook and evidence references
evals/results/
└── supabase-migration-*.json  # generated non-secret verification evidence
```

**Structure Decision**: Keep the repository's existing Alembic and SQL checks as the canonical schema contract. Add only an operations runbook, a machine-readable evidence contract, and generated evidence; do not duplicate schema definitions in application code or introduce a second ORM migration system.

## Complexity Tracking

No constitution violations identified.

## Post-Design Constitution Check

PASS. The design keeps the remote write bounded, auditable, project-scoped, and reversible through the existing ordered migration history. Data transfer remains a separately approved operation.
