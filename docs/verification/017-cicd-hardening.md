# Feature 017 — CI/CD hardening

| Check | Result |
|---|---:|
| Workflow YAML parse | **passed** for `ci.yml` and `evals.yml` |
| Docker Compose config | **passed** (`docker compose config --quiet`) |
| Evaluation unit gate | **20 passed** |
| Exact CI mypy gate (`mypy src tests`) | **passed: 383 files checked with zero diagnostics** |
| Backend pytest from CI working directory | **428 passed, 4 skipped** |
| Fresh database job | **passed locally on 2026-08-11:** an isolated empty database reached `agent_tool_rls` and all 19 versioned SQL contract files passed with `ON_ERROR_STOP` |
| Browser job | workflow installs Chromium and runs Playwright; report uploads only on failure |
| Provider secrets | no OpenAI/LangSmith secret is required by PR CI |
| Security regression paths | **14 passed** using the corrected repository-root path |
| Deployment contract paths | **7 passed** using the corrected repository-root paths |
| Deterministic offline evaluation | **46/46 passed** with execution mode `deterministic-fixture` |
| CI 768 px browser regression | **7/7 affected routes passed** after the responsive AppShell breakpoint correction |

## Hosted CI regression repaired on 2026-08-11

The failing hosted database job was reproduced locally against an isolated empty database named
`atlas_ci_verify`. Migration `0026_supabase_extension_security` assumed Supabase's managed
`extensions` schema already existed. The local/CI pgvector image installs `vector` in `public` and
does not create that schema. The migration now creates `extensions` with `IF NOT EXISTS` before
moving pgvector. This leaves an already-correct Supabase database unchanged and makes the versioned
migration chain self-contained for fresh environments.

The hosted security and deployment-contract jobs also used paths relative to `apps/backend` while
executing from the repository root. The workflow now uses complete `apps/backend/tests/...` paths,
and its global `PYTHONPATH` points to `apps/backend/src`. Hosted-run identifiers are recorded only
after the corrected commit completes on GitHub Actions.

The first corrected hosted run then exposed two later integration regressions: new agent tests had
not been added to the existing strict typing baseline, and the offline evaluator needs both
`apps/backend/src` and the repository root on `PYTHONPATH`. The test fixtures now use the actual
typed domain models and explicit return types rather than weakening mypy. CI includes both import
roots. Local closeout is Ruff clean, mypy clean across 383 files, 428 backend tests passed with 4
environment skips, and all 46 deterministic evaluation cases passed.

The browser job's public check annotations identified seven failures, all caused by the same 768 px
header overflow: the desktop navigation remained active until 720 px and pushed the locale control
55 px beyond the viewport. The compact navigation breakpoint is now 840 px. The seven affected
home, comparison, report, news, sources, account, and admin routes pass the focused Playwright matrix.
The complete rerun against a prebuilt Next production server reports **150 passed and 6 hosted-only
smoke skips** out of 156 tests. CI now builds before Playwright and tests `next start`, avoiding
development-server compilation races while retaining a separate failing build boundary.

## Hosted CI and branch protection verified on 2026-08-11

Commit `87043701acf964038884b974414eb9528c5eb18b` completed GitHub Actions run
[`31489992776`](https://github.com/JhonyKing/atlas/actions/runs/31489992776), Offline Evaluation run
[`31489992707`](https://github.com/JhonyKing/atlas/actions/runs/31489992707), Supabase migration run
[`31489992706`](https://github.com/JhonyKing/atlas/actions/runs/31489992706), and the Vercel preview
successfully. The nine merge-gating checks all concluded `success`: `backend`, `cited-answer-v1`,
`database`, `Deployment contracts and secret boundary`, `offline-eval`,
`Repository and evidence contracts`, `security-regression`, `Vercel`, and `web`.

This PR also supplies real failure-path evidence. The first Supabase workflow run
[`31489718182`](https://github.com/JhonyKing/atlas/actions/runs/31489718182) failed because its test
step used backend-relative paths while executing at repository root. The failed required check
blocked merge. Commit `8704370` corrected the paths, the exact local suite passed **25/25**, and the
replacement hosted run passed. The protection was not bypassed or weakened.

Authenticated repository administration then set `main` as the default branch and enabled branch
protection with strict required checks, an enforced pull-request boundary, stale-review dismissal,
admin enforcement, linear history, and required conversation resolution. Force-pushes and branch
deletion are disabled. The approval count is intentionally zero because this is currently a
single-maintainer portfolio repository: a PR and all checks remain mandatory without requiring the
author to manufacture an unavailable second reviewer.

The redacted settings snapshot, failed-gate record, correction, and hosted-run identifiers are preserved in
[`github-main-protection-20260811.json`](../../evals/results/github-main-protection-20260811.json).
This closes the previously external branch-protection and hosted-run evidence gap without claiming
that the still-unprovisioned managed API/worker deployment is production-ready.
