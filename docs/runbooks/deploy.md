# Deployment runbook

1. Build from an immutable commit or release tag.
2. Run all CI gates, including deterministic RAG evals and secret scanning.
3. Run `scripts/release-migrate.ps1 -DryRun`, then apply the forward-only migration in the target.
4. Deploy the API/worker image and Vercel web with environment-scoped secrets.
5. Wait for `/healthz` and `/readyz`; run `scripts/deployment-smoke.py`.
6. Attach the redacted release evidence artifact to the release. Never paste secrets into logs.
