# Feature 017 architecture

CI is split into backend, security, web, database and offline-evaluation jobs. The database job
starts a fresh PostgreSQL/pgvector service, applies migrations, runs every SQL contract with
fail-fast semantics and verifies the migration head. The web job installs pinned Node/pnpm
dependencies, runs lint/typecheck/unit/build and Playwright journeys. Evaluation artifacts label
deterministic fixture mode so they cannot be mistaken for live RAG quality.
