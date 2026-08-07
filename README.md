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

## Feature 004: optional authentication and private data

Feature 004 adds optional sign-in without breaking anonymous use. Authenticated sessions are held
in an HttpOnly cookie, private resources are checked by owner in the API and PostgreSQL RLS, and
uploads are validated, quarantined, scanned, and only then allowed to become indexable. Deletion
requests are repeat-safe through idempotency keys. The UI defaults to Spanish (`es-MX`) and keeps
English labels available.

The executable source of truth is:

- `specs/004-optional-auth-private-data/spec.md`
- `specs/004-optional-auth-private-data/plan.md`
- `specs/004-optional-auth-private-data/tasks.md`
- `specs/004-optional-auth-private-data/quickstart.md`
- `docs/architecture/004-identity-private-data.md`
- `docs/adr/0003-optional-auth-boundary.md`

Run the local verification from the repository root:

```powershell
.\scripts\verify-auth.ps1
pnpm --filter @atlas/web lint
pnpm --filter @atlas/web typecheck
pnpm --filter @atlas/web test:e2e -- --project=chromium
```

Apply the database migrations with Docker PostgreSQL running, then execute the four SQL contracts
listed in the feature quickstart. The complete recorded evidence is in
`docs/verification/004-auth-private-data.md`.

## Feature 005: expanded curated corpus and ingestion governance

Feature 005 adds a governed catalog of 16 approved collections (10 frameworks and 6 model
providers), bounded HTTPS host/path validation, deterministic GitHub, scholarly, pricing and
private-content connector seams, HTML/Markdown/PDF normalization, immutable source versions,
staleness and seven-day coverage reporting, policy/takedown state transitions, retry/dead-letter
tracking, and redacted run telemetry. Private records remain tenant-scoped and are never promoted
to the public corpus.

The source of truth and evidence are:

- `specs/005-expanded-curated-corpus/spec.md`
- `specs/005-expanded-curated-corpus/plan.md`
- `specs/005-expanded-curated-corpus/tasks.md`
- `docs/architecture/005-ingestion-governance.md`
- `docs/adr/0004-curated-corpus-governance.md`
- `docs/verification/005-expanded-curated-corpus.md`

Run the deterministic verification from the repository root:

```powershell
pnpm test:ingestion
```

## Feature 006: agent graph, checkpoints, and human review

Feature 006 adds a deterministic typed orchestration boundary for classification and planning,
explicit answer/comparison/report/abstention routes, content-safe thread checkpoints with
single-use replay, and a bilingual human-review gate before publication. The API exposes planning,
review decisions, checkpoint status, and resume without returning request bodies or private state.

Source and evidence:

- `specs/006-agent-graph-human-review/spec.md`
- `specs/006-agent-graph-human-review/tasks.md`
- `docs/architecture/006-agent-graph-human-review.md`
- `docs/adr/0005-explicit-agent-orchestration.md`
- `docs/verification/006-agent-graph-human-review.md`

```powershell
pnpm test:agent
```

## Feature 007: retrieval quality and multilingual evidence

Feature 007 keeps the original question intact while adding bounded aliases, version/date/language
filters, deterministic source diversity, parent context windows and a hard evidence budget. An
optional reranker is evaluated beside the baseline and is not enabled after a quality, latency or
cost regression.

Source and evidence:

- `specs/007-retrieval-quality-multilingual/spec.md`
- `specs/007-retrieval-quality-multilingual/tasks.md`
- `docs/architecture/007-retrieval-quality-multilingual.md`
- `docs/adr/0006-measured-retrieval-quality.md`
- `docs/verification/007-retrieval-quality-multilingual.md`
- `evals/cases/007-retrieval-quality-multilingual.jsonl`

```powershell
pnpm test:retrieval
apps\backend\.venv\Scripts\python.exe -m atlas.evaluation.retrieval_quality `
  --dataset evals/cases/007-retrieval-quality-multilingual.jsonl `
  --output docs/verification/007-retrieval-quality-multilingual-metrics.json
```
