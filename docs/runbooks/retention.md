# Runbook: anonymous-content retention

## Normal operation

The migration seeds `atlas.retention_jobs` with `interaction_retention` at `0 2 * * *` UTC. A
worker invokes the bounded function; local development can execute the same contract directly:

```powershell
$env:PGPASSWORD = "atlas-local-only"
psql "postgresql://atlas@localhost:55432/atlas" -c "SELECT * FROM atlas.purge_expired_interactions(now(), 100);"
```

The function aggregates first, deletes in small locked batches, and returns a batch key plus the
remaining expired count. Repeating it is safe: deleted runs are absent and existing tombstones do
not duplicate aggregate rows.

## Verify privacy invariants

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'atlas' AND table_name = 'daily_metrics';

SELECT count(*) FROM atlas.answer_runs WHERE expires_at <= now();
SELECT count(*) FROM atlas.answer_run_tombstones;
```

`daily_metrics` must not contain `visitor_key_hash`, `answer_run_id`, `question`, URLs, or free
text. Run `database/tests/005_retention.sql` after any retention migration change.

## Incident response

If batches stop progressing, inspect PostgreSQL availability and the returned
`remaining_expired_count`. Do not delete corpus tables to force progress. Restore the scheduler,
rerun the function, and verify the tombstone/aggregate contract; all content deletion is scoped to
expired answer runs.
