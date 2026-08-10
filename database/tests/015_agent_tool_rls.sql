-- Feature 019 durable agent tables must have explicit RLS and worker/read-only policies.
DO $$
DECLARE
  table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'agent_plans',
    'agent_runs',
    'agent_tool_calls',
    'agent_run_events',
    'agent_approvals',
    'agent_idempotency_records',
    'agent_checkpoint_claims'
  ] LOOP
    IF NOT EXISTS (
      SELECT 1
      FROM pg_class AS c
      JOIN pg_namespace AS n ON n.oid = c.relnamespace
      WHERE n.nspname = 'atlas'
        AND c.relname = table_name
        AND c.relrowsecurity
    ) THEN
      RAISE EXCEPTION 'RLS is not enabled for atlas.%', table_name;
    END IF;
    IF NOT EXISTS (
      SELECT 1
      FROM pg_policies
      WHERE schemaname = 'atlas'
        AND tablename = table_name
        AND policyname = table_name || '_worker_all'
    ) THEN
      RAISE EXCEPTION 'Worker policy is missing for atlas.%', table_name;
    END IF;
    IF NOT EXISTS (
      SELECT 1
      FROM pg_policies
      WHERE schemaname = 'atlas'
        AND tablename = table_name
        AND policyname = table_name || '_readonly_select'
    ) THEN
      RAISE EXCEPTION 'Readonly policy is missing for atlas.%', table_name;
    END IF;
  END LOOP;
END $$;
