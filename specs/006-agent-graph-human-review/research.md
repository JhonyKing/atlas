# Research Notes: Feature 006

- The repository already has an explicit `CitedAnswerGraph`; Feature 006 should extend its state and
  lifecycle rather than introduce an autonomous loop.
- Existing answer/report ownership and evidence verification are the publication boundaries; review
  must call those validators instead of duplicating them.
- Existing observability uses redacted structured events and a LangSmith sink; node events should
  use the same content-free policy.
- PostgreSQL migrations and RLS are already the durable persistence convention; deterministic tests
  use in-memory adapters to avoid live provider credentials.
