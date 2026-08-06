# Implementation Plan: Evidence-backed Research Reports

**Branch**: `003-reports` | **Date**: 2026-08-06 | **Spec**: [spec.md](spec.md)

## Summary

Implement the first report vertical slice from a completed technology-comparison run to a
validated, bilingual DOCX/PDF artifact with citations, lifecycle control, and a final documentation
closure task. The design keeps the existing evidence graph authoritative: report generation may
plan narrative text, but it cannot create evidence IDs or replace source excerpts.

## Technical Context

**Language/Version**: Python 3.13, TypeScript/Node 24

**Primary Dependencies**: FastAPI, Pydantic, PostgreSQL/Alembic, python-docx, ReportLab or a
PDF conversion seam, Next.js, Playwright

**Storage**: PostgreSQL metadata plus local artifact storage for the first slice

**Testing**: pytest contract/unit/integration tests, TypeScript/Vitest, Playwright, DOCX/PDF
parseability checks, render-and-inspect visual QA, deterministic report evaluation cases

**Target Platform**: Local development and GitHub-hosted Linux CI; no production deployment in
this feature

**Project Type**: Monorepo web application/API with asynchronous job coordination

**Performance Goals**: 95% of supported report jobs complete within 60 seconds in the portfolio
workload; downloads begin within 2 seconds after completion

**Constraints**: No provider secrets in tests; no raw source instructions in prompts; citation IDs,
URLs, and original excerpts must remain unchanged across locales; artifact files must be bounded and
retained for 30 days by default

**Scale/Scope**: First slice supports one completed comparison run, five report types in the
contract, DOCX/PDF output, two locales, anonymous ownership, and a separate report quota

## Constitution Check

- **Evidence Over Fluency**: PASS. Report claims are assembled from source-run evidence and fail
  closed when sections lack citations.
- **Spec Before Code**: PASS. This spec, plan, data model, contract, quickstart, tasks, and analyze
  artifacts precede implementation.
- **Test and Evaluate First**: PASS. Renderer integrity, citation linkage, lifecycle, and bilingual
  parity tests are required before implementation tasks are marked complete.
- **Explicit Contracts and Type Safety**: PASS. Report request/status/download schemas are versioned
  in `contracts/report-api.yaml` and validated at the API boundary.
- **Provider Independence**: PASS. Narrative planning uses the existing answer-generator port; file
  rendering and validation remain provider-independent.
- **Security and Privacy**: PASS. Ownership uses the existing visitor digest; storage paths and
  provider credentials never enter user-visible responses.
- **Observable and Cost-Aware**: PASS. Report jobs carry request ID, source run, model/prompt
  versions, corpus snapshot, latency, size, and content hash metadata.
- **Small Vertical Slices**: PASS. Technology comparison is the first complete report type; the
  remaining catalog stays behind the same ReportSpec boundary.

## Research Summary

See [research.md](research.md). Decisions:

1. Use the completed comparison run as the first source boundary; do not invent a second research
   persistence model.
2. Persist report metadata and lifecycle state separately from binary artifacts.
3. Create one structured intermediate representation and render both DOCX and PDF from it.
4. Validate generated files structurally and visually before publishing the completed state.
5. Keep live LangSmith/report-quality evaluation outside the first synchronous CI gate; add fixture
   report cases and artifact snapshots in this feature.

## Data Model and Contracts

- Entity rules: [data-model.md](data-model.md)
- HTTP/SSE contract: [contracts/report-api.yaml](contracts/report-api.yaml)
- Validation path: [quickstart.md](quickstart.md)

## Project Structure

```text
apps/backend/src/atlas/reports/
├── schemas.py              # ReportSpec, ReportJob, ReportDocument, ReportSection
├── service.py              # quota, ownership, idempotency, lifecycle
├── planner.py              # source-run to structured report representation
├── renderers/docx.py       # DOCX rendering seam
├── renderers/pdf.py        # PDF rendering seam
├── validation.py           # file, citation, link, and render checks
└── storage.py              # artifact metadata and bounded local storage
apps/backend/src/atlas/api/routes/reports.py
apps/backend/tests/contract/reports/
apps/backend/tests/unit/reports/
apps/web/src/features/reports/
database/migrations/versions/0016_reports.py
database/tests/008_reports.sql
evals/datasets/report-v1.jsonl
docs/architecture/003-reports.md
docs/adr/0002-evidence-backed-report-boundary.md
```

## Implementation Sequence

1. Write failing report schemas, ownership/idempotency tests, citation-link tests, and renderer
   integrity fixtures.
2. Add the report metadata schema/migration and repository/service lifecycle.
3. Add comparison-run planning and structured sections with fail-closed citation checks.
4. Add DOCX/PDF renderers and structural/render validation.
5. Add API routes, SSE progress, frontend report controls, download/delete/expiry behavior, and
   bilingual parity.
6. Run the full verification matrix and report evaluation cases.
7. **Documentation closure (mandatory final task)**: read the final `spec.md`, `plan.md`,
   `tasks.md`, actual diff, and commit history; update README, relevant ADRs, and architecture docs
   only for delivered behavior, then run link/consistency checks.

## Complexity Tracking

| Decision | Simpler alternative rejected because |
|---|---|
| Separate report metadata from artifacts | Binary files alone cannot support ownership, expiry, idempotency, or reproducibility metadata. |
| One intermediate report representation for DOCX/PDF | Separate format-specific planning would create citation and locale drift. |
| Async job contract in the first slice | Rendering and future report types need cancellation, retries, and progress without changing the public API. |

