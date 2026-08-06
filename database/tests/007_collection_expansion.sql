-- Collection expansion contract: Anthropic is fourth, Gemini fifth, and both are catalogued.
DO $$
DECLARE
  total_collections integer;
  anthropic_present boolean;
  gemini_present boolean;
BEGIN
  SELECT count(*) INTO total_collections FROM atlas.collections;
  IF total_collections < 5 THEN
    RAISE EXCEPTION 'expected at least five catalogued collections, got %', total_collections;
  END IF;

  SELECT EXISTS(SELECT 1 FROM atlas.collections WHERE slug = 'anthropic') INTO anthropic_present;
  SELECT EXISTS(SELECT 1 FROM atlas.collections WHERE slug = 'gemini') INTO gemini_present;
  IF NOT anthropic_present OR NOT gemini_present THEN
    RAISE EXCEPTION 'anthropic and gemini must be catalogued';
  END IF;

  BEGIN
    INSERT INTO atlas.collections(
      slug, display_name, publisher, base_url, allowed_hosts
    ) VALUES ('invalid-provider', 'Invalid', 'Invalid', 'https://invalid.example/', ARRAY['invalid.example']);
    RAISE EXCEPTION 'unsupported collection slug was accepted';
  EXCEPTION WHEN check_violation THEN
    NULL;
  END;
END $$;
