"""Add privacy-preserving anonymous answer quota reservation."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_anonymous_quota"
down_revision = "0002_corpus_ingestion"
branch_labels = None
depends_on = None


_RESERVE_FUNCTION = """
CREATE OR REPLACE FUNCTION atlas.reserve_answer_quota(
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
  IF p_idempotency_key IS NULL OR length(p_idempotency_key) = 0 THEN
    RAISE EXCEPTION 'idempotency key must not be blank';
  END IF;
  PERFORM pg_advisory_xact_lock(hashtextextended(p_visitor_key_hash, 0));
  SELECT u.answer_run_id, u.remaining_after, u.accepted_at
  INTO existing_run_id, existing_remaining, existing_accepted_at
  FROM atlas.usage_events AS u
  WHERE u.visitor_key_hash = p_visitor_key_hash
    AND u.idempotency_key = p_idempotency_key;
  IF FOUND THEN
    RETURN QUERY SELECT true, existing_run_id, existing_remaining, existing_accepted_at,
      NULL::timestamptz;
    RETURN;
  END IF;
  SELECT count(*)::integer, min(u.accepted_at)
  INTO accepted_count, oldest_accepted_at
  FROM atlas.usage_events AS u
  WHERE u.visitor_key_hash = p_visitor_key_hash
    AND u.accepted_at > observed_at - interval '24 hours';
  IF accepted_count >= 10 THEN
    RETURN QUERY SELECT false, NULL::uuid, 0, NULL::timestamptz,
      oldest_accepted_at + interval '24 hours';
    RETURN;
  END IF;
  INSERT INTO atlas.usage_events(
    visitor_key_hash, idempotency_key, answer_run_id, accepted_at, expires_at,
    remaining_after
  ) VALUES (
    p_visitor_key_hash, p_idempotency_key, p_run_id, observed_at,
    observed_at + interval '30 days', 10 - accepted_count - 1
  );
  RETURN QUERY SELECT true, p_run_id, 10 - accepted_count - 1, observed_at,
    NULL::timestamptz;
END
$$;
"""


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.usage_events (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              visitor_key_hash char(64) NOT NULL CHECK (visitor_key_hash ~ '^[0-9a-f]{64}$'),
              idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 16 AND 128),
              answer_run_id uuid NOT NULL,
              accepted_at timestamptz NOT NULL,
              expires_at timestamptz NOT NULL,
              remaining_after integer NOT NULL CHECK (remaining_after BETWEEN 0 AND 9),
              UNIQUE (visitor_key_hash, idempotency_key),
              UNIQUE (answer_run_id)
            );
            CREATE INDEX IF NOT EXISTS usage_events_visitor_accepted_idx
              ON atlas.usage_events(visitor_key_hash, accepted_at);
            """
        )
    )
    op.execute(sa.text(_RESERVE_FUNCTION))


def downgrade() -> None:
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.reserve_answer_quota(text, text, uuid, timestamptz)"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.usage_events"))
