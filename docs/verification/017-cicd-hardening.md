# Feature 017 — CI/CD hardening

| Check | Result |
|---|---:|
| Workflow YAML parse | **passed** for `ci.yml` and `evals.yml` |
| Docker Compose config | **passed** (`docker compose config --quiet`) |
| Evaluation unit gate | **20 passed** |
| Fresh database job | workflow runs Alembic to head, then all SQL contracts with `ON_ERROR_STOP` |
| Browser job | workflow installs Chromium and runs Playwright; report uploads only on failure |
| Provider secrets | no OpenAI/LangSmith secret is required by PR CI |

The repository controls workflow checks. GitHub branch protection (required checks, approvals and
direct-push policy) must still be verified in repository settings; it cannot be proven by a local
workflow parse.
