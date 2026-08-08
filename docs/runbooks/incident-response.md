# Incident response runbook

1. Check `/healthz` (process liveness) and `/readyz` (database, migration, provider, and
   observability checks) without exposing response bodies that contain secrets.
2. Correlate the `X-Request-ID`, release ID, source revision, and migration revision in logs and
   redacted LangSmith traces.
3. Freeze promotion, preserve the release evidence artifact, and decide whether to roll back the
   immutable web/API versions using `docs/runbooks/rollback.md`.
4. If the database is involved, do not downgrade migrations blindly; use the expand/contract
   compatibility procedure and the backup/restore runbook.
5. Record timeline, impact, checks, decision owner, and follow-up action in the incident record.
