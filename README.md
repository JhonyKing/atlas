# ATLAS AI

ATLAS is an evidence-first technical research application. The executable source of truth for
each feature is its SpecKit directory under `specs/`.

## Feature 003: reports

The current vertical slice accepts a completed technology-comparison run and plans a citation-
preserving report. The backend exposes report job lifecycle routes under `/v1/reports`, renders
both DOCX and PDF from one neutral representation, validates that artifacts contain their evidence
manifest, and supports bilingual presentation (`en-US` and `es-MX`). Local artifacts are bounded
and expire after 30 days; ownership and idempotency are enforced at the API boundary.
Each job also records model, prompt-version, source-run, and corpus-snapshot metadata for
reproducibility.

Run the focused verification from the repository root:

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/reports apps/backend/tests/contract/api/test_reports.py -q
```

The public contract and implementation work remain tracked in:

- `specs/003-reports/spec.md`
- `specs/003-reports/plan.md`
- `specs/003-reports/tasks.md`
- `specs/003-reports/contracts/report-api.yaml`
- `docs/architecture/003-reports.md`
- `docs/adr/0002-evidence-backed-report-boundary.md`

This first slice does not claim the remaining report catalog or live LangSmith report-quality
evaluation is complete; those tasks stay open in `tasks.md`.
