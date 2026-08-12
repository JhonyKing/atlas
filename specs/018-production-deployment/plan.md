# Implementation Plan: Production Deployment

**Branch**: `018-production-deployment` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

## Summary

Create a reproducible beta deployment path for ATLAS. Vercel hosts the Next.js web application;
Supabase provides the managed PostgreSQL/pgvector/Auth/Storage target; a managed container runtime
hosts the FastAPI API and ingestion worker. The repository will contain environment contracts,
container/release configuration, migration gates, smoke tests, release evidence, observability and
rollback runbooks. A public deployment is not considered complete until a real environment passes
the evidence bundle checks.

## Technical Context

**Language/Version**: Python 3.13, Node 24, TypeScript strict, YAML/PowerShell

**Primary Dependencies**: FastAPI/Uvicorn, Alembic, PostgreSQL/pgvector, Supabase Auth/Storage,
Next.js 16, Vercel build/runtime, managed container runtime, GitHub Actions, LangSmith/OpenTelemetry

**Storage**: Local PostgreSQL/pgvector for development and CI; isolated Supabase PostgreSQL/pgvector,
Auth, and Storage for preview/staging/production

**Testing**: pytest, Ruff, mypy, Vitest, Playwright, SQL contracts, deterministic RAG evals,
deployment readiness/smoke runner, secret scan

**Target Platform**: Vercel for web; managed HTTPS container runtime for API/worker; Supabase for data

**Project Type**: Monorepo web application, API, worker, and deployment automation

**Performance Goals**: Preserve existing SLO instrumentation; readiness is bounded; no beta claim
without evidence for 99.5% availability, TTFT p50 <1.5s, normal p95 <12s, reports <3 minutes,
uncontrolled errors <1%, citation rate >=95%, and per-task cost budgets

**Constraints**: No secrets in source/client/logs; preview isolation; forward-compatible migrations;
no destructive automatic down-migrations; local workflow remains usable; deployment credentials are
operator-provided; backend cannot rely on Vercel function limits

**Scale/Scope**: Portfolio beta, bounded traffic, small approved corpus first; one reproducible
preview/staging path and one production path

## Constitution Check

- Evidence Over Fluency: PASS - release evidence and smoke results are required; no runtime claim from a green build alone.
- Spec Before Code: PASS - this feature has spec, checklist, plan, contracts, quickstart, and path-specific tasks.
- Test and Evaluate First: PASS - release gates include failing-contract tests, migration checks, browser checks, evals, and smoke tests.
- Explicit Contracts and Type Safety: PASS - readiness and release-evidence schemas are versioned artifacts.
- Provider Independence with Measured Routing: PASS - Supabase/Vercel/runtime are adapters; domain contracts remain portable.
- Security and Privacy by Design: PASS - environment separation, secret boundaries, RLS, redaction, and fail-closed readiness are explicit.
- Observable and Cost-Aware: PASS - release and request evidence includes traces, latency, cost, and redaction checks.
- Small Vertical Slices Before Scale: PASS - start with a bounded beta and one end-to-end deployment path.
- English-Canonical Engineering: PASS - code/contracts/docs are English; locale behavior is tested as product output.

## Project Structure

```text
specs/018-production-deployment/
  spec.md, plan.md, research.md, data-model.md, quickstart.md
  contracts/deployment-readiness.md
  contracts/release-evidence.schema.json
  checklists/requirements.md
.github/workflows/             # release and deployment gates
infra/                          # container, environment, migration and platform manifests
scripts/                        # readiness, smoke, secret and evidence commands
apps/backend/                   # API and worker image/runtime
apps/web/                       # Vercel web project
docs/architecture/              # deployment ADR and runbooks
evals/results/                  # redacted release/eval evidence only
```

**Structure Decision**: Keep deployment orchestration in `infra/`, `.github/workflows/`, and
`scripts/`. Keep provider-specific configuration at the edge and reuse existing API/web/domain
contracts. Do not add a second domain or duplicate data model for Supabase.

**Interim beta activation**: An owner-approved Vercel Python Function may host the HTTP API
entrypoint for the portfolio beta while the full managed API/worker runtime remains pending. This
is a bounded activation adapter for the cited-answer web flow, not a replacement for the
long-running worker architecture or the Feature 018 Definition of Done.

## Implementation Sequence

1. Add failing contracts for environment separation, readiness, release evidence, secret scanning,
   and deployment smoke behavior.
2. Add platform-neutral container and environment configuration for API/worker and the Vercel web.
3. Add Supabase migration/connection/RLS validation and explicit release migration step.
4. Add CI/CD release gates, immutable evidence bundle, health checks, and rollback controls.
5. Configure operator-owned Vercel, Supabase, domain, container, model, and LangSmith values in a
   non-production environment and run the quickstart.
6. Verify observability, backups/restore, bilingual smoke journeys, and rollback rehearsal.
7. Update README, ADRs, deployment runbooks, PRD backlog, and feature status; run Speckit analyze
   and converge before closing.

## Complexity Tracking

| Item | Why needed | Simpler alternative rejected because |
|---|---|---|
| Separate API/worker container runtime | Existing backend includes long-running and scheduled work | Vercel-only functions would impose the wrong runtime contract |
| Release evidence bundle | Portfolio and operations require externally verifiable deployment proof | A dashboard screenshot cannot prove migrations, smoke paths, or redaction |
