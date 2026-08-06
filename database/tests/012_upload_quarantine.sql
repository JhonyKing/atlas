-- Feature 004 quarantine contract: unsafe content cannot become searchable.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'atlas' AND table_name = 'private_upload_chunks'
  ) THEN
    IF EXISTS (
      SELECT 1 FROM atlas.private_uploads u
      JOIN atlas.private_upload_chunks c ON c.upload_id = u.id
      WHERE u.scan_status = 'rejected'
    ) THEN
      RAISE EXCEPTION 'rejected upload has searchable chunks';
    END IF;
  END IF;
END $$;

SELECT scan_status, parse_status, count(*)
FROM atlas.private_uploads
GROUP BY scan_status, parse_status;
