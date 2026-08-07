# Scale and reliability runbook

1. Capture commit, environment, workload version and database migration head.
2. Run `pnpm test:slo` and inspect missing-metric failures.
3. For a live run, record availability, p95, TTFT, report duration, uncontrolled errors, citation
   precision and cost. Do not infer capacity from a passing unit test.
4. If a gate fails, stop promotion, preserve the metric artifact, inspect traces by request/run ID,
   and roll back the affected release or provider configuration.
5. Backups, alerts and external load tests are deployment responsibilities and must be attached to
   the same evidence record.
