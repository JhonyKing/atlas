# Feature 017 — CI/CD hardening

| Check | Result |
|---|---:|
| Workflow YAML parse | **passed** for `ci.yml` and `evals.yml` |
| Docker Compose config | **passed** (`docker compose config --quiet`) |
| Evaluation unit gate | **20 passed** |
| Exact CI mypy gate (`mypy src tests`) | **passed: 314 files checked with zero diagnostics** |
| Backend pytest from CI working directory | **304 passed, 4 skipped** |
| Fresh database job | **passed locally on 2026-08-11:** an isolated empty database reached `agent_tool_rls` and all 19 versioned SQL contract files passed with `ON_ERROR_STOP` |
| Browser job | workflow installs Chromium and runs Playwright; report uploads only on failure |
| Provider secrets | no OpenAI/LangSmith secret is required by PR CI |
| Security regression paths | **14 passed** using the corrected repository-root path |
| Deployment contract paths | **7 passed** using the corrected repository-root paths |

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

The repository controls workflow checks. GitHub branch protection (required checks, approvals and
direct-push policy) must still be verified in repository settings; it cannot be proven by a local
workflow parse. The repository-controlled implementation and local verification are complete;
branch-protection settings remain external evidence.
