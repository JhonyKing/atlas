# Beta readiness checklist (PRD SCL-011)

- [ ] Vercel preview and production URLs, API alias, and public-access evidence are recorded in
      `environments.md`.
- [ ] Vercel Production contains `CRON_SECRET` and provider secrets, and the five per-collection
      Cron routes are configured from the approved scheduled-ingestion branch.
- [ ] Supabase project ref, migration head `comparison_pricing_contract` (33 revisions), pgvector,
      Auth, Storage, pooling, and RLS evidence are recorded.
- [ ] CORS, model-provider readiness, and LangSmith safe tags/redaction are verified without
      exposing credentials or private payloads.
- [ ] Deterministic RAG gate, one bounded run for each collection, and hosted bilingual smoke
      evidence are attached to the release.
- [ ] Correlated redacted traces, availability/latency/error/cost/citation alerts are verified.
- [ ] Non-production backup/restore rehearsal and rollback rehearsal are recorded; production
      restore is not claimed without evidence.
- [ ] Operator signs off only after T031-T036 and T052 evidence is complete; local Docker is not
      evidence of beta readiness. An always-on worker runtime is not required by the approved beta.
