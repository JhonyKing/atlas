# ATLAS AI

ATLAS is an evidence-first technical research application. The executable source of truth for
each feature is its SpecKit directory under `specs/`.

## Feature 018: production deployment foundation

The repository now contains the production deployment contract: Vercel web configuration,
provider-neutral API/worker container and manifest, Supabase migration preflight, `/healthz`
liveness, `/readyz` dependency readiness, deployment smoke checks, CI release gates, redacted
release evidence, and deploy/backup/rollback runbooks. This is a deployable foundation, not a
claim that the complete managed runtime is already live. The web is published at
[`https://atlasai-lilac.vercel.app`](https://atlasai-lilac.vercel.app); the managed API/worker is not
live yet, so the complete product is not declared production-ready.

Local checks:

```powershell
$env:PYTHONPATH='apps/backend/src'
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests -q
apps\backend\.venv\Scripts\python.exe scripts\deployment-smoke.py --help
```

Remaining deployment tasks: create isolated preview/staging Supabase targets, provision the managed
API/worker, configure environment secrets and API origin, run bilingual functional smoke tests,
verify LangSmith redaction, rehearse backup/restore and rollback, and attach the release evidence
bundle. The exact checklist is in `specs/018-production-deployment/tasks.md`.

## Feature 021: Supabase database migration

The PostgreSQL schema is reproducibly migrated to the project-scoped Supabase production project
`fcbclsaytbjpywlaplbh` through OAuth-authenticated MCP operations. The repository remains the
schema source of truth; local fixtures and private/user rows are not copied by default. The
current remote head is `agent_tool_rls` (31 hosted revisions). The repository now contains a
32nd reviewed candidate, `foreign_key_indexes`, which resolves the hosted unindexed-foreign-key
advisor findings; it has passed fresh-database validation but is not yet applied to production.

The repeatable verification workflow lives in `scripts/supabase/` and is enforced by
`.github/workflows/supabase-migration.yml`. Pull requests run manifest, evidence-contract, and
provider-neutral workflow tests. Remote comparison is read-only and requires an owner-provided
MCP snapshot; no GitHub Action applies migrations or receives a service-role key.

Source, operations, and verification:

- `specs/021-supabase-database-migration/spec.md`
- `specs/021-supabase-database-migration/tasks.md`
- `docs/runbooks/supabase-migration.md`
- `docs/adr/0013-supabase-development-migration.md`
- `docs/verification/021-supabase-migration.md`

### Latest hosted Supabase update (2026-08-11)

The owner-approved `agent_tool_rls` migration is now applied in production. The remote head is
`agent_tool_rls` at 31 revisions. Seven durable agent tables have FORCE RLS, 14 reviewed
worker/read-only policies, and no `anon`/`authenticated` grants. Supabase still reports 41 other
`atlas` tables without RLS; those require a separate reviewed policy plan.

Evidence: `evals/results/supabase-migration-agent-tool-rls-20260811-applied.json`. The earlier
blocked attempt remains preserved at `evals/results/supabase-migration-agent-tool-rls-20260810.json`.

The next migration, `0032_foreign_key_indexes.py`, adds 24 covering indexes without changing row
data or RLS. Local evidence: ordered 32-revision manifest, fresh-database migration, SQL contract,
Ruff, strict mypy, and **428 passed / 4 skipped** backend tests. Production remains at revision 31
until the owner explicitly approves this new production write.

## Feature 019: agent tool orchestration

ATLAS exposes its capabilities as a versioned, typed tool catalog. The agent can propose a bounded
plan, preview the selected tool and arguments, request explicit approval for private or consequential
actions, execute read-only domain adapters, and display ordered run events with evidence/artifact
counts. When an OpenAI key is configured, GPT-5.6 Luna produces a structured proposal through the
provider adapter; an outage uses the bounded deterministic fallback. Provider output never
authorizes a tool. Every registered tool also runs behind its catalog timeout and plan-level call
and evidence budgets; cancellation and partial failure remain visible in the run timeline.

Run the deterministic verification from the repository root:

```powershell
.\scripts\verify-agent-tools.ps1
```

The source of truth and evidence are `specs/019-agent-tool-orchestration/`,
`docs/architecture/019-agent-tool-orchestration.md`, `docs/adr/0014-agent-tool-orchestration.md`,
and `docs/verification/019-agent-tool-orchestration.md`.

The latest content-free live trace evidence is
[`evals/results/agent-tool-live-evidence-20260811.json`](evals/results/agent-tool-live-evidence-20260811.json).
It covers successful, abstained, rejected, failed, cancelled, and resumed journeys with opaque
IDs and bounded latency/outcome metadata. Provider token and cost fields remain
`not_reported` when the configured provider does not expose them.

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

## Feature 008: model router, GPT-5.6 Luna, and cost controls

The router defaults to `gpt-5.6-luna`, selects reasoning effort from typed task signals, and keeps
provider SDK details behind an adapter port. Timeout/retry/circuit policies, effective-dated
pricing, daily budgets, redacted cost records, versioned cache keys, embedding fallback and A/B
promotion gates are covered by deterministic tests.

Source and evidence:

- `specs/008-model-router-gpt56-luna/tasks.md`
- `docs/architecture/008-model-router-gpt56-luna.md`
- `docs/adr/0007-model-router-luna-and-cost-gates.md`
- `docs/verification/008-model-router-gpt56-luna.md`
- `evals/cases/008-model-router-gpt56-luna.jsonl`

```powershell
pnpm test:model-router
```

## Feature 009: security, privacy, and governance hardening

Feature 009 adds source/redirect SSRF checks, inert-source and action allowlists, redacted audit and
trace boundaries, consent/no-training policy, tenant-safe private data behavior, rate-limit
challenge handling, frontend secret scanning and a CI security regression job.

Evidence and design:

- `specs/009-security-privacy-governance/tasks.md`
- `docs/architecture/009-security-privacy-governance.md`
- `docs/adr/0008-security-boundaries-and-private-data.md`
- `docs/verification/009-security-privacy-governance.md`
- `docs/security/external-review.md`

```powershell
pnpm test:security
```

## Feature 010: scale, reliability, and SLOs

Feature 010 adds fail-closed SLO gates for availability, errors, latency, TTFT, report duration,
citation precision and cost. The workload fixture covers read, answer, report, ingestion and launch
spike scenarios; it does not claim live load capacity.

- `specs/010-scale-reliability-slos/tasks.md`
- `docs/architecture/010-scale-reliability-slos.md`
- `docs/adr/0009-evidence-driven-scale-gates.md`
- `docs/verification/010-scale-reliability-slos.md`

```powershell
pnpm test:slo
```

## Feature 011: evaluation and quality loop

Feature 011 unifies deterministic schema, citation, retrieval, freshness and report checks with
versioned judge contracts, online security/anomaly signals, safe trace tags and fail-closed quality
gates. Public methodology contains aggregates only.

- `specs/011-evaluation-quality-loop/tasks.md`
- `docs/architecture/011-evaluation-quality-loop.md`
- `docs/adr/0010-deterministic-quality-before-judges.md`
- `docs/verification/011-evaluation-quality-loop.md`
- `docs/quality/public-methodology.md`

```powershell
pnpm test:evals
pnpm test:eval-regression
```

## Feature 012: portfolio productization and proof

The portfolio layer indexes setup, architecture, ADRs, measured baselines, KPIs, interview
narrative and external-evidence limitations. It deliberately separates verified local artifacts
from work that requires participants, live load, a video or an external review.

- `docs/portfolio/architecture-map.md`
- `docs/portfolio/baseline-comparison.md`
- `docs/portfolio/kpis.json`
- `docs/portfolio/evidence-ledger.json`
- `docs/portfolio/interview-narrative.md`
- `docs/portfolio/external-evidence.md`

```powershell
pnpm test:portfolio
```

## Feature 001: cited-answer quickstart evidence

The local quickstart baseline is recorded in `evals/results/001-cited-answer-baseline.md` and the
machine-readable evaluator output in `evals/results/001-cited-answer-baseline.json`. It covers
Docker/PostgreSQL migration, API contract checks, frontend lint/typecheck and deterministic
46-case evaluation. The five-person usability study and seven-day refresh period are external
acceptance evidence and remain visibly pending.

## Feature 020: UX/UI and brand redesign

Feature 020 gives ATLAS a route-owned AppShell, bilingual navigation, consistent brand assets,
responsive public research surfaces, explicit account/admin boundaries, and inspectable
loading, empty, error, and unavailable states. It is a visual/product-design slice: it does
not change backend behavior or claim that a provider is available in the frontend-only preview.

### Route map

| Surface | Routes |
| --- | --- |
| Ask and evidence | `/`, `/en`, `/es` |
| Comparator | `/compare`, `/en/compare`, `/es/compare` |
| Reports | `/reports`, `/en/reports`, `/es/reports` |
| Previous-day news | `/news`, `/en/news`, `/es/news` |
| Corpus sources | `/sources`, `/en/sources`, `/es/sources` |
| Optional auth/private data | `/account`, `/en/account`, `/es/account` |
| Internal operations | `/admin`, `/admin/sources`, `/admin/reviews`, `/admin/governance` and localized equivalents |

### Design system and brand assets

- Tokens, typography, spacing, radii, focus treatment, state colors, and responsive rules live in
  `apps/web/src/app/globals.css`.
- Route composition and locale switching live in `apps/web/src/components/layout/AppShell.tsx`.
- Source SVG logos are in `apps/web/public/brand/`; transparent PNG fallbacks are generated with
  `pnpm --filter @atlas/web brand:generate`.
- The app uses `atlas-mark.png` for compact/mobile identity and the horizontal SVG/PNG lockup for
  wider navigation contexts. Favicon and Apple touch metadata are defined in the root layout.

### Regression closeout

The final Feature 020 regression record is **35/35 frontend unit tests**, **149 Playwright tests
passed with 4 hosted-deployment skips**, and **379 backend tests passed with 4 skips**. The four
Playwright skips require a configured deployed origin and are intentionally not represented as
local product failures.

### UX and visual evidence

- `docs/verification/020-final-visual-review.md` — second visual-only review and resolutions.
- `docs/verification/020-production-build.md` — production build and responsive smoke evidence.
- `docs/verification/020-visual-matrix.md` — 49-case accessibility/visual matrix.
- `docs/verification/020-route-states.md` — 10 empty/error/retry state checks.
- `apps/web/tests/e2e/visual-qa-routes.spec.ts` — 60 bilingual route screenshots at 1440x900 and 390x844.
- `specs/020-ux-ui-brand-redesign/tasks.md` — SpecKit source of truth and Definition of Done.

Run the frontend checks from the repository root:

```powershell
pnpm typecheck
pnpm lint
pnpm test
pnpm build
```

For the production visual matrix, use the built server explicitly:

```powershell
$env:CI = "1"
$env:ATLAS_PROD_SERVER = "1"
pnpm --filter @atlas/web exec playwright test tests/visual/viewport-matrix.spec.ts --workers=4 --retries=0
```
