-- Reserve one anonymous comparison under a separate five-per-24-hour window.
CREATE OR REPLACE FUNCTION atlas.reserve_comparison_quota(
  p_visitor_key_hash text,
  p_idempotency_key text,
  p_run_id uuid,
  p_now timestamptz DEFAULT now()
) RETURNS TABLE(
  accepted boolean,
  run_id uuid,
  remaining integer,
  accepted_at timestamptz,
  retry_at timestamptz
)
LANGUAGE plpgsql
AS $$
DECLARE
  existing_run_id uuid;
  existing_remaining integer;
  existing_accepted_at timestamptz;
  accepted_count integer;
  oldest_accepted_at timestamptz;
  observed_at timestamptz := p_now;
BEGIN
  IF p_visitor_key_hash !~ '^[0-9a-f]{64}$' THEN
    RAISE EXCEPTION 'visitor key hash must be a lowercase SHA-256 digest';
  END IF;
  IF p_idempotency_key IS NULL OR length(p_idempotency_key) NOT BETWEEN 16 AND 128 THEN
    RAISE EXCEPTION 'comparison idempotency key must contain 16 to 128 characters';
  END IF;

  PERFORM pg_advisory_xact_lock(hashtextextended(p_visitor_key_hash, 1));

  SELECT u.comparison_run_id, u.remaining_after, u.accepted_at
  INTO existing_run_id, existing_remaining, existing_accepted_at
  FROM atlas.comparison_usage_events AS u
  WHERE u.visitor_key_hash = p_visitor_key_hash
    AND u.idempotency_key = p_idempotency_key
    AND u.accepted_at > observed_at - interval '24 hours';
  IF FOUND THEN
    RETURN QUERY SELECT true, existing_run_id, existing_remaining, existing_accepted_at,
      NULL::timestamptz;
    RETURN;
  END IF;

  SELECT count(*)::integer, min(u.accepted_at)
  INTO accepted_count, oldest_accepted_at
  FROM atlas.comparison_usage_events AS u
  WHERE u.visitor_key_hash = p_visitor_key_hash
    AND u.accepted_at > observed_at - interval '24 hours';

  IF accepted_count >= 5 THEN
    RETURN QUERY SELECT false, NULL::uuid, 0, NULL::timestamptz,
      oldest_accepted_at + interval '24 hours';
    RETURN;
  END IF;

  INSERT INTO atlas.comparison_usage_events(
    visitor_key_hash, idempotency_key, comparison_run_id, accepted_at,
    expires_at, remaining_after
  ) VALUES (
    p_visitor_key_hash, p_idempotency_key, p_run_id, observed_at,
    observed_at + interval '30 days', 5 - accepted_count - 1
  );
  RETURN QUERY SELECT true, p_run_id, 5 - accepted_count - 1, observed_at,
    NULL::timestamptz;
END
$$;
