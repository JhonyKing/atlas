# Beta readiness checklist (PRD SCL-011)

- [ ] Vercel preview and production URLs recorded in `environments.md`.
- [ ] API/worker HTTPS endpoint and immutable image digest recorded.
- [ ] Supabase targets, migration head, pgvector, Auth, Storage, pooling, and RLS evidence recorded.
- [ ] Environment-scoped secrets, CORS, auth callbacks, model provider, and LangSmith tags verified.
- [ ] Deterministic RAG gate and hosted bilingual smoke evidence attached to the release.
- [ ] Correlated redacted traces, availability/latency/error/cost/citation alerts verified.
- [ ] Non-production backup/restore rehearsal and rollback rehearsal recorded.
- [ ] Operator signs off only after T030-T036 evidence is complete; local Docker is not evidence of beta readiness.
