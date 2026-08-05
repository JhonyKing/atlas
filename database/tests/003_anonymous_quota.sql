-- T035/T036: anonymous identity quota contract tests.
\set ON_ERROR_STOP on

DO $$
BEGIN
  IF to_regclass('atlas.usage_events') IS NULL THEN
    RAISE EXCEPTION 'atlas.usage_events table is missing';
  END IF;
  IF to_regprocedure('atlas.reserve_answer_quota(text,text,uuid,timestamptz)') IS NULL THEN
    RAISE EXCEPTION 'atlas.reserve_answer_quota function is missing';
  END IF;
END
$$;

BEGIN;
DO $$
DECLARE visitor_hash text := repeat('d', 64);
DECLARE now_at timestamptz := '2026-08-04 12:00:00+00';
DECLARE run_id uuid;
DECLARE first_run_id uuid;
DECLARE accepted boolean;
DECLARE remaining integer;
DECLARE retry_at timestamptz;
DECLARE index integer;
BEGIN
  FOR index IN 0..9 LOOP
    INSERT INTO atlas.answer_runs(
      visitor_key_hash, idempotency_key, question, status, expires_at
    ) VALUES (
      visitor_hash,
      'quota-answer-run-' || lpad(index::text, 3, '0'),
      'How does the quota work?',
      'accepted',
      now_at + interval '30 days'
    ) RETURNING id INTO run_id;
    IF index = 0 THEN
      first_run_id := run_id;
    END IF;
    SELECT q.run_id, q.accepted, q.remaining INTO run_id, accepted, remaining
    FROM atlas.reserve_answer_quota(
      visitor_hash, 'quota-test-key-' || lpad(index::text, 3, '0'), run_id, now_at
    ) AS q;
    IF NOT accepted OR remaining <> 9 - index THEN
      RAISE EXCEPTION 'reservation % did not consume one slot', index;
    END IF;
  END LOOP;

  SELECT q.accepted, q.retry_at INTO accepted, retry_at
  FROM atlas.reserve_answer_quota(visitor_hash, 'quota-test-key-010', atlas.new_uuid(), now_at) AS q;
  IF accepted OR retry_at <> now_at + interval '24 hours' THEN
    RAISE EXCEPTION 'eleventh reservation did not return exact retry time';
  END IF;

  SELECT q.run_id, q.remaining INTO run_id, remaining
  FROM atlas.reserve_answer_quota(visitor_hash, 'quota-test-key-000', first_run_id, now_at) AS q;
  IF remaining <> 9 THEN
    RAISE EXCEPTION 'idempotent retry consumed another quota unit';
  END IF;
END
$$;
ROLLBACK;

SELECT 'anonymous quota contract passed' AS result;
