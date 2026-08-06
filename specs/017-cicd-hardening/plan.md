# Implementation Plan: CI/CD Hardening

**Branch**: `017-cicd-hardening` | **Date**: 2026-08-06 | **Spec**: [spec.md](spec.md)

## Summary

Close the highest-impact CI gaps identified in the repository audit: prove fresh-database
migrations and SQL contracts, run the existing Playwright suite in the web job, and preserve the
deterministic-versus-live evaluation boundary in artifacts. No provider secrets or deployment
side effects are introduced.

## Technical Context

**Language/Version**: GitHub Actions YAML, Python 3.13, Node 24

**Primary Dependencies**: uv/Alembic, Docker Compose, pnpm/Playwright

**Storage**: PostgreSQL 17 with pgvector

**Testing**: Alembic upgrade, psql SQL contracts, pytest, Vitest, Playwright, deterministic eval CLI

**Target Platform**: GitHub-hosted Ubuntu runners

**Project Type**: Monorepo web application and API

**Performance Goals**: CI remains bounded and fails fast on migration, contract, browser, or eval errors

**Constraints**: No OpenAI/LangSmith credentials; pinned lockfiles; no production deployment

**Scale/Scope**: Pull requests and pushes to `main`; one PostgreSQL service and existing test suite

## Constitution Check

- Evidence Over Fluency: PASS — evaluation artifacts distinguish deterministic fixtures from live results.
- Spec Before Code: PASS — this feature has a spec, plan, tasks, and checklist before workflow edits.
- Test and Evaluate First: PASS — workflow changes are validated with local migration/contracts and existing tests.
- Explicit Contracts and Type Safety: PASS — SQL contracts and existing static checks remain explicit.
- Security and Privacy: PASS — no secrets or external provider calls are added.
- Small Vertical Slices: PASS — this slice changes only CI validation, not deployment.

## Project Structure

```text
.github/workflows/ci.yml                 # database and browser gates
specs/017-cicd-hardening/                 # feature decision record
database/tests/                           # versioned SQL contracts
```

**Structure Decision**: Keep CI orchestration in the existing workflows and reuse existing
migrations, SQL contracts, and browser tests instead of adding a second test framework.

## Implementation Sequence

1. Add a fresh-database migration and SQL-contract sequence to the existing database job.
2. Add Playwright browser installation and execution to the existing web job.
3. Run local static checks, backend tests, evaluator, and workflow syntax review.
4. Mark completed tasks with command evidence and commit the vertical slice.

## Complexity Tracking

No constitution violations.
