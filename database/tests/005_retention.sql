-- T067: 30-day retention, aggregate preservation, batching, and idempotency.
\set ON_ERROR_STOP on

DO $$
BEGIN
  IF to_regclass('atlas.daily_metrics') IS NULL THEN
    RAISE EXCEPTION 'atlas.daily_metrics table is missing';
  END IF;
  IF to_regclass('atlas.answer_run_tombstones') IS NULL THEN
    RAISE EXCEPTION 'atlas.answer_run_tombstones table is missing';
  END IF;
  IF to_regprocedure('atlas.purge_expired_interactions(timestamptz,integer)') IS NULL THEN
    RAISE EXCEPTION 'atlas.purge_expired_interactions function is missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM atlas.retention_jobs
    WHERE name = 'interaction_retention'
      AND cron_expression = '0 2 * * *'
      AND status = 'enabled'
  ) THEN
    RAISE EXCEPTION 'daily interaction retention schedule is missing';
  END IF;
END
$$;

BEGIN;
DO $$
DECLARE
  observed_at timestamptz := '2026-08-04 12:00:00+00';
  visitor_hash text := repeat('a', 64);
  run_id uuid;
  first_purged integer;
  second_purged integer;
  third_purged integer;
  first_batch text;
  first_metrics record;
  second_metrics record;
BEGIN
  INSERT INTO atlas.answer_runs(
    visitor_key_hash, idempotency_key, question, status, answer_status,
    model_provider, model_id, input_tokens, output_tokens, estimated_cost_usd,
    latency_ms, created_at, expires_at
  ) VALUES
    (visitor_hash, 'retention-test-key-001', 'First retained question', 'completed', 'complete',
      'openai', 'gpt-5.6-luna', 10, 5, 0.012345, 100,
      observed_at - interval '31 days', observed_at - interval '1 day'),
    (visitor_hash, 'retention-test-key-002', 'Second retained question', 'abstained', 'abstained',
      'openai', 'gpt-5.6-luna', 20, 10, 0.023456, 200,
      observed_at - interval '31 days', observed_at - interval '1 day'),
    (visitor_hash, 'retention-test-key-003', 'Third retained question', 'failed', NULL,
      'openai', 'gpt-5.6-luna', 30, 15, 0.087655, 300,
      observed_at - interval '31 days', observed_at - interval '1 day');

  SELECT purged_count, batch_key INTO first_purged, first_batch
  FROM atlas.purge_expired_interactions(observed_at, 2);
  IF first_purged <> 2 OR first_batch IS NULL OR length(first_batch) = 0 THEN
    RAISE EXCEPTION 'retention must purge exactly two rows and return a batch key';
  END IF;

  SELECT purged_count INTO second_purged
  FROM atlas.purge_expired_interactions(observed_at, 2);
  IF second_purged <> 1 THEN
    RAISE EXCEPTION 'retention must process the remaining expired row in a later batch';
  END IF;

  SELECT purged_count INTO third_purged
  FROM atlas.purge_expired_interactions(observed_at, 2);
  IF third_purged <> 0 THEN
    RAISE EXCEPTION 'retention retry must be idempotent';
  END IF;

  SELECT
    coalesce(sum(accepted_count), 0) AS accepted_count,
    coalesce(sum(completed_count), 0) AS completed_count,
    coalesce(sum(abstained_count), 0) AS abstained_count,
    coalesce(sum(error_count), 0) AS error_count,
    coalesce(sum(input_tokens), 0) AS input_tokens,
    coalesce(sum(output_tokens), 0) AS output_tokens,
    coalesce(sum(estimated_cost_usd), 0) AS estimated_cost_usd,
    coalesce(sum(latency_sum_ms), 0) AS latency_sum_ms,
    coalesce(sum(latency_sample_count), 0) AS latency_sample_count
  INTO first_metrics
  FROM atlas.daily_metrics
  WHERE metric_date = (observed_at - interval '31 days')::date;

  IF first_metrics.accepted_count <> 3
     OR first_metrics.completed_count <> 1
     OR first_metrics.abstained_count <> 1
     OR first_metrics.error_count <> 1
     OR first_metrics.input_tokens <> 60
     OR first_metrics.output_tokens <> 30
     OR first_metrics.estimated_cost_usd <> 0.123456
     OR first_metrics.latency_sum_ms <> 600
     OR first_metrics.latency_sample_count <> 3 THEN
    RAISE EXCEPTION 'retention aggregate rollup is incorrect: %', first_metrics;
  END IF;

  SELECT count(*) INTO second_metrics FROM atlas.answer_runs WHERE idempotency_key LIKE 'retention-test-key-%';
  IF second_metrics.count <> 0 THEN
    RAISE EXCEPTION 'expired answer content was not deleted';
  END IF;
  SELECT count(*) INTO second_metrics FROM atlas.answer_run_tombstones WHERE purged_at <= observed_at;
  IF second_metrics.count <> 3 THEN
    RAISE EXCEPTION 'expired run tombstones were not preserved';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'atlas' AND table_name = 'daily_metrics'
      AND column_name IN ('visitor_key_hash', 'answer_run_id', 'question')
  ) THEN
    RAISE EXCEPTION 'daily metrics must not contain user or content dimensions';
  END IF;
END
$$;

ROLLBACK;

SELECT 'retention contract passed' AS result;
