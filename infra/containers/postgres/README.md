# Local PostgreSQL

The development container provides PostgreSQL 17 and pgvector with a deterministic health check.
Schema ownership, `pg_cron`, `pgmq`, least-privilege roles, and application migrations are added by
the foundational database tasks rather than hidden in container initialization.
