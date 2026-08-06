-- Feature 004 cross-user ownership policy contract.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'atlas' AND tablename = 'ownership_grants' AND policyname = 'ownership_subject'
  ) THEN
    RAISE EXCEPTION 'missing ownership RLS policy';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'atlas' AND tablename = 'private_uploads' AND policyname = 'uploads_subject'
  ) THEN
    RAISE EXCEPTION 'missing private upload RLS policy';
  END IF;
END $$;

SELECT policyname, tablename FROM pg_policies
WHERE schemaname = 'atlas' AND tablename IN ('users','sessions','ownership_grants');
