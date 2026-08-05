-- Delete expired anonymous interaction content after preserving content-free aggregates.
CREATE OR REPLACE FUNCTION atlas.purge_expired_interactions(
  p_now timestamptz DEFAULT now(),
  p_batch_size integer DEFAULT 100
) RETURNS TABLE(
  purged_count integer,
  batch_key text,
  remaining_expired_count integer
)
LANGUAGE plpgsql
AS $$
DECLARE
  expired_run record;
  processed integer := 0;
  remaining integer := 0;
  current_batch_key text := format(
    'retention:%s:%s',
    to_char(p_now AT TIME ZONE 'UTC', 'YYYYMMDDHH24MISSMS'),
    md5(random()::text || clock_timestamp()::text)
  );
  citation_total bigint;
  useful_total bigint;
BEGIN
  IF p_batch_size IS NULL OR p_batch_size < 1 OR p_batch_size > 1000 THEN
    RAISE EXCEPTION 'retention batch size must be between 1 and 1000';
  END IF;

  FOR expired_run IN
    SELECT
      run.id,
      run.status,
      run.model_id,
      run.input_tokens,
      run.output_tokens,
      run.estimated_cost_usd,
      run.latency_ms,
      run.created_at,
      run.expires_at
    FROM atlas.answer_runs AS run
    WHERE run.expires_at <= p_now
    ORDER BY run.expires_at, run.id
    LIMIT p_batch_size
    FOR UPDATE SKIP LOCKED
  LOOP
    SELECT count(*) INTO citation_total
    FROM atlas.answer_citations
    WHERE answer_run_id = expired_run.id;

    SELECT count(*) INTO useful_total
    FROM atlas.feedback
    WHERE answer_run_id = expired_run.id
      AND label = 'useful';

    INSERT INTO atlas.daily_metrics(
      metric_date,
      dimension_key,
      accepted_count,
      completed_count,
      abstained_count,
      error_count,
      quota_denied_count,
      useful_count,
      citation_count,
      input_tokens,
      output_tokens,
      estimated_cost_usd,
      latency_sum_ms,
      latency_sample_count
    ) VALUES (
      expired_run.created_at::date,
      left(coalesce(nullif(expired_run.model_id, ''), 'unknown'), 64),
      1,
      CASE WHEN expired_run.status = 'completed' THEN 1 ELSE 0 END,
      CASE WHEN expired_run.status = 'abstained' THEN 1 ELSE 0 END,
      CASE WHEN expired_run.status = 'failed' THEN 1 ELSE 0 END,
      0,
      useful_total,
      citation_total,
      coalesce(expired_run.input_tokens, 0),
      coalesce(expired_run.output_tokens, 0),
      coalesce(expired_run.estimated_cost_usd, 0),
      coalesce(expired_run.latency_ms, 0),
      CASE WHEN expired_run.latency_ms IS NULL THEN 0 ELSE 1 END
    )
    ON CONFLICT (metric_date, dimension_key) DO UPDATE SET
      accepted_count = atlas.daily_metrics.accepted_count + EXCLUDED.accepted_count,
      completed_count = atlas.daily_metrics.completed_count + EXCLUDED.completed_count,
      abstained_count = atlas.daily_metrics.abstained_count + EXCLUDED.abstained_count,
      error_count = atlas.daily_metrics.error_count + EXCLUDED.error_count,
      quota_denied_count = atlas.daily_metrics.quota_denied_count + EXCLUDED.quota_denied_count,
      useful_count = atlas.daily_metrics.useful_count + EXCLUDED.useful_count,
      citation_count = atlas.daily_metrics.citation_count + EXCLUDED.citation_count,
      input_tokens = atlas.daily_metrics.input_tokens + EXCLUDED.input_tokens,
      output_tokens = atlas.daily_metrics.output_tokens + EXCLUDED.output_tokens,
      estimated_cost_usd = atlas.daily_metrics.estimated_cost_usd + EXCLUDED.estimated_cost_usd,
      latency_sum_ms = atlas.daily_metrics.latency_sum_ms + EXCLUDED.latency_sum_ms,
      latency_sample_count = atlas.daily_metrics.latency_sample_count + EXCLUDED.latency_sample_count;

    INSERT INTO atlas.answer_run_tombstones(answer_run_id, expired_at, purged_at, batch_key)
    VALUES (expired_run.id, expired_run.expires_at, p_now, current_batch_key)
    ON CONFLICT (answer_run_id) DO NOTHING;

    DELETE FROM atlas.answer_runs WHERE id = expired_run.id;
    processed := processed + 1;
  END LOOP;

  SELECT count(*) INTO remaining
  FROM atlas.answer_runs
  WHERE expires_at <= p_now;

  RETURN QUERY SELECT processed, current_batch_key, remaining;
END
$$;
