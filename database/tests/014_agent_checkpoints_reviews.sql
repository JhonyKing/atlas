-- Feature 006 checkpoint/review schema contract.
DO $$
DECLARE table_name_value text;
BEGIN
  FOREACH table_name_value IN ARRAY ARRAY[
    'agent_checkpoints','agent_review_requests','agent_review_decisions'
  ] LOOP
    IF to_regclass('atlas.' || table_name_value) IS NULL THEN
      RAISE EXCEPTION 'missing agent table atlas.%', table_name_value;
    END IF;
  END LOOP;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'agent_checkpoints_thread_id_replay_key_key'
  ) THEN
    RAISE EXCEPTION 'checkpoint replay uniqueness is missing';
  END IF;
END $$;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'atlas' AND table_name LIKE 'agent_%'
ORDER BY table_name;
