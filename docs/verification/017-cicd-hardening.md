# Feature 017 — CI/CD hardening

| Check | Result |
|---|---:|
| Workflow YAML parse | **passed** for `ci.yml` and `evals.yml` |
| Docker Compose config | **passed** (`docker compose config --quiet`) |
| Evaluation unit gate | **20 passed** |
| Exact CI mypy gate (`mypy src tests`) | **failed: 140 diagnostics**; strict annotations and existing protocol/type mismatches remain |
| Backend pytest from CI working directory | **304 passed, 4 skipped** |
| Fresh database job | workflow runs Alembic to head, then all SQL contracts with `ON_ERROR_STOP` |
| Browser job | workflow installs Chromium and runs Playwright; report uploads only on failure |
| Provider secrets | no OpenAI/LangSmith secret is required by PR CI |

The repository controls workflow checks. GitHub branch protection (required checks, approvals and
direct-push policy) must still be verified in repository settings; it cannot be proven by a local
workflow parse. Feature 017 is therefore not fully closed until the mypy debt is resolved or a
reviewed baseline policy is added without weakening type safety.
