# ATLAS AI PRD v1.1 — backlog maestro ejecutable

Este backlog convierte el PRD en trabajo trazable. Cada épica debe comenzar con el ciclo Spec Kit:
`/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` →
`/speckit.analyze` → pruebas → `/speckit.implement` → `/speckit.converge`.

Una tarea de este archivo no autoriza saltar la especificación de su feature. La tarea inicial de
cada épica crea esa especificación y las tareas detalladas de implementación se generan allí.

## Foundation and product control (feature 000)

- [ ] RDM-001 Extract and version the PRD v1.1 requirements and maintain `docs/product/prd-v1.1-traceability.md`.
- [ ] RDM-002 Create the product-level Spec Kit roadmap for the twelve PRD weeks and decision gates.
- [ ] RDM-003 Define the portfolio MVP cut line: cited answer, bilingual UX, corpus status, evals, and one report vertical slice.
- [ ] RDM-004 Record ADR-007 (English canonical + Spanish parity), ADR-008 (Spec Kit), and ADR-009 (Next.js/TypeScript + Python).
- [ ] RDM-005 Keep the repository structure map synchronized with the implemented monorepo; document intentional deviations from the PRD tree.

## 001 — cited answer and bilingual public journey

- [X] CAV-001–CAV-073 Implement the cited-answer, evidence, abstention, retention, corpus-status, evaluation, and documentation baseline (existing tasks T001–T073).
- [ ] CAV-074 Run the five-person usability study and record locale, task outcome, and defects.
- [ ] CAV-075 Run the seven-day refresh validation.
- [ ] CAV-076 Execute the quickstart baseline.
- [ ] CAV-077 Finish README portfolio handoff.
- [ ] CAV-078 Add failing tests for locale routing, `en-US`/`es-MX` catalog parity, preference persistence, and language-independent citations.
- [ ] CAV-079 Implement localized `/en` and `/es` routes, message catalogs, locale switch, preference persistence, and locale formatting.
- [ ] CAV-080 Propagate locale through API requests and return localized controlled errors/statuses without translating evidence IDs or URLs.
- [ ] CAV-081 Translate all cited-answer, evidence, corpus-status, feedback, progress, quota, cancellation, and abstention UI copy.
- [ ] CAV-082 Add CORS preflight tests and a deterministic development runtime that works without a provider key; keep production provider wiring strict.
- [ ] CAV-083 Re-run analyze/converge and update this matrix with the remaining gap list.

## 002 — technology comparator

- [ ] CMP-001 Run `/speckit.specify` for configurable 2–4 technology comparison with explicit criteria and evidence per cell.
- [ ] CMP-002 Specify supported criteria: capability, tool calling, context, latency, price, license, freshness, and operational risk.
- [ ] CMP-003 Plan comparison state, retrieval fan-out, normalization, missing-value semantics, and contradiction handling.
- [ ] CMP-004 Write contract, domain, retrieval, and accessible UI tests before implementation.
- [ ] CMP-005 Implement comparison request and asynchronous progress flow.
- [ ] CMP-006 Implement evidence-backed comparison matrix and claim-level citations for every populated cell.
- [ ] CMP-007 Implement criterion selection, source/date/version filters, and unsupported-cell explanation.
- [ ] CMP-008 Add deterministic dataset cases for two-, three-, and four-technology comparisons.
- [ ] CMP-009 Add Playwright journey and regression gate; prove the comparator is not a generic chat response.

## 003 — reports, ADRs, and document artifacts

- [ ] RPT-001 Run `/speckit.specify` for asynchronous report generation from an existing research run.
- [ ] RPT-002 Specify report types: technology comparison, architecture brief, ADR, release intelligence, and research report.
- [ ] RPT-003 Plan neutral `ReportSpec`, section schemas, citation policy, artifact storage, job state, and retry/idempotency semantics.
- [ ] RPT-004 Write JSON-schema, authorization, queue, render, citation, and artifact-integrity tests before implementation.
- [ ] RPT-005 Implement report planning and validated intermediate JSON with audience, scope, criteria, and required sections.
- [ ] RPT-006 Implement DOCX renderer with cover, executive summary, analysis, recommendation, risks, costs, implementation plan, and references.
- [ ] RPT-007 Implement PDF rendering and visual QA; fail a release on clipping, overflow, missing citations, or invalid links.
- [ ] RPT-008 Implement asynchronous progress, artifact retention, resumable jobs, and repeat-safe download.
- [ ] RPT-009 Implement EN/ES renderers with semantic and citation parity; original excerpts remain clearly marked.
- [ ] RPT-010 Add report quota separate from anonymous cited-answer quota.
- [ ] RPT-011 Add ten structured report evaluation cases and artifact regression snapshots.
- [ ] RPT-012 Add user-facing report summary, download, delete, and expired-artifact semantics.

## 004 — optional authentication, sessions, uploads, and private data

- [ ] IDN-001 Run `/speckit.specify` for optional authentication and per-user data ownership.
- [ ] IDN-002 Plan anonymous-to-authenticated migration without changing anonymous quota semantics.
- [ ] IDN-003 Write Auth, RLS, session, upload, report-ownership, and deletion tests first.
- [ ] IDN-004 Implement login/logout/session renewal and optional profile preferences.
- [ ] IDN-005 Implement threads, saved conversations, run history, and locale preference persistence.
- [ ] IDN-006 Implement private uploads with file/type/size/malware checks and tenant boundaries.
- [ ] IDN-007 Implement RLS for threads, uploads, reports, feedback, and artifact metadata.
- [ ] IDN-008 Implement account/data deletion and audit evidence.
- [ ] IDN-009 Add Playwright journeys for anonymous use, sign-in, ownership, and deletion.

## 005 — expanded curated corpus and ingestion governance

- [ ] ING-001 Run `/speckit.specify` for expanded sources while preserving the allowlist boundary.
- [ ] ING-002 Add connector specs for 10–15 frameworks and 6–8 model providers.
- [ ] ING-003 Add GitHub Releases/changelog connector with 6–24 hour schedule.
- [ ] ING-004 Add OpenAlex/Semantic Scholar metadata connector and paper links.
- [ ] ING-005 Add official pricing/model-list snapshots with change detection.
- [ ] ING-006 Add authorized user-content connector with private tenant storage.
- [ ] ING-007 Implement sitemap/API/versioned-page discovery and bounded fetch policies.
- [ ] ING-008 Implement HTML/Markdown/PDF normalization that preserves headings, tables, and code blocks.
- [ ] ING-009 Implement source panel coverage/freshness/disabled-state reporting.
- [ ] ING-010 Implement metadata: canonical URL, title, author/org, published/captured dates, license, hash.
- [ ] ING-011 Implement version relation, staleness/TTL, and historical-vs-current classification.
- [ ] ING-012 Implement robots/ToS/license review gates and source enablement approval.
- [ ] ING-013 Implement takedown/correction workflow and atomic source disablement.
- [ ] ING-014 Add per-collection retry, dead-letter, preservation, and re-review trigger tests.
- [ ] ING-015 Validate the full refresh and coverage dashboard against the seven-day operational target.

## 006 — agent graph, planning, checkpoints, and human review

- [ ] AGT-001 Run `/speckit.specify` for router/planner/retrieval/verifier/answer/report graph orchestration.
- [ ] AGT-002 Specify `AtlasState`: messages, user, request, intent, language, freshness, plan, evidence, citations, answer, report, quality, errors.
- [ ] AGT-003 Plan conditional edges, explicit deterministic nodes, model boundaries, and failure paths.
- [ ] AGT-004 Write node-order, state-isolation, timeout, cancellation, and routing tests before implementation.
- [ ] AGT-005 Implement intent/depth/language/risk/freshness classification.
- [ ] AGT-006 Implement question decomposition and source/date criteria planning.
- [ ] AGT-007 Implement report path with validated `report_spec` and pause-before-sensitive-action.
- [ ] AGT-008 Implement persistent checkpoints keyed by `thread_id` for long-running report/ingestion/eval jobs.
- [ ] AGT-009 Implement resume-after-worker-failure and idempotent replay tests.
- [ ] AGT-010 Implement human review approve/edit/reject boundary for publication or consequential actions.

## 007 — retrieval quality and multilingual evidence

- [ ] RET-001 Run `/speckit.specify` for production retrieval quality beyond the exact hybrid baseline.
- [ ] RET-002 Implement query rewriting for terms, versions, aliases, and synonyms.
- [ ] RET-003 Implement filters for provider, framework, date, version, language, and source type.
- [ ] RET-004 Implement MMR/deduplication diversity and parent-child context windows.
- [ ] RET-005 Implement measured reranking/cross-encoder behind an adapter, only after baseline comparison.
- [ ] RET-006 Benchmark multilingual embeddings and language-aware retrieval.
- [ ] RET-007 Implement evidence-budget token limits and authority/freshness prioritization.
- [ ] RET-008 Add Hit@5, MRR, context precision/recall, citation precision, and freshness accuracy evals.
- [ ] RET-009 Add temporal, cross-language, contradiction, and source-version regression cases.

## 008 — model router, GPT-5.6 Luna, and cost controls

- [ ] MOD-001 Run `/speckit.specify` for provider-independent model routing and fallback.
- [ ] MOD-002 Make `gpt-5.6-luna` the configured primary model for the ATLAS answer path, with explicit model/version telemetry.
- [ ] MOD-003 Define model selection by task complexity, freshness, contradiction, and report depth.
- [ ] MOD-004 Implement adapters for the approved providers without importing SDK details into graph nodes.
- [ ] MOD-005 Implement timeout, retry-with-jitter, circuit breaker, and provider fallback behavior.
- [ ] MOD-006 Implement multilingual embedding provider selection without changing Evidence schema.
- [ ] MOD-007 Implement effective-dated price tables, token/cost telemetry, daily budget, and alerts.
- [ ] MOD-008 Add cache/evidence-pack policy for repeated questions and provider context caching where available.
- [ ] MOD-009 Add batch path for ingestion, labelling, and offline evals.
- [ ] MOD-010 Add model benchmark and A/B evaluation gate; never select a model by unverified marketing claims.

## 009 — security, privacy, and governance hardening

- [ ] SEC-001 Run `/speckit.specify` for private data and production security controls.
- [ ] SEC-002 Write threat-model tests for SSRF, redirects, source injection, unauthorized tools, and generated-code execution.
- [ ] SEC-003 Implement secrets-only-in-secret-manager deployment checks and frontend secret scanning.
- [ ] SEC-004 Implement RLS and least-privilege roles for all private entities.
- [ ] SEC-005 Implement upload malware/type/size scanning and scheduled deletion.
- [ ] SEC-006 Implement IP/user/API-key rate limiting and abuse challenge boundary.
- [ ] SEC-007 Implement audit log for source, report, admin, and sensitive-action changes.
- [ ] SEC-008 Implement clear privacy notice and account/data deletion mechanism.
- [ ] SEC-009 Implement no-training-on-private-documents policy and consent records.
- [ ] SEC-010 Implement redacted traces, PII checks, retention/tombstones, and irreversible aggregates.
- [ ] SEC-011 Add security regression gate to CI.
- [ ] SEC-012 Run pre-launch external security review and resolve critical findings.

## 010 — scale, reliability, and launch SLOs

- [ ] SCL-001 Run `/speckit.specify` for measured MVP→beta→growth scale path.
- [ ] SCL-002 Implement connection pooling and observed indexed SQL queries.
- [ ] SCL-003 Measure Redis/queue need before adding infrastructure; keep long jobs out of web requests.
- [ ] SCL-004 Add HNSW/iterative-filter benchmark only when exact-search measurements justify it.
- [ ] SCL-005 Implement retrieval/answer cache with source-version invalidation.
- [ ] SCL-006 Implement circuit breakers, timeouts, jitter retries, and provider fallback load tests.
- [ ] SCL-007 Separate anonymous and authenticated/premium endpoint limits.
- [ ] SCL-008 Run read, answer, report, ingestion, and launch-spike load scenarios.
- [ ] SCL-009 Measure 99.5% API availability, TTFT p50 <1.5 s, normal p95 <12 s, report <3 min, uncontrolled errors <1%.
- [ ] SCL-010 Validate citation rate ≥95% and cost budget by task type.
- [ ] SCL-011 Produce beta deployment, domain, analytics, backups, alerts, and runbooks.
- [ ] SCL-012 Produce scale decision record for 10k/100k MAU; do not claim capacity without evidence.

## 011 — evaluation, observability, and quality loop

- [ ] EVA-001 Run `/speckit.specify` for the complete evaluation lifecycle.
- [ ] EVA-002 Expand golden dataset to 25 factual, 20 temporal, 15 comparative, 10 abstention, 10 injection, 10 report, and 10 bilingual cases.
- [ ] EVA-003 Implement deterministic schema/link/length/duplicate/report-structure evaluators.
- [ ] EVA-004 Implement retrieval metrics and freshness evaluator.
- [ ] EVA-005 Implement generation faithfulness/relevance/completeness/clarity/utility judge with bias controls.
- [ ] EVA-006 Implement citation entailment, version correctness, and source sufficiency evaluator.
- [ ] EVA-007 Implement human feedback/annotation queue and difficult-case review.
- [ ] EVA-008 Implement online security/format/anomaly/latency/cost evaluators.
- [ ] EVA-009 Run regression sample on every prompt/retrieval/model/chunking change.
- [ ] EVA-010 Block deploy on citation, hallucination, schema, cost, or latency threshold regressions.
- [ ] EVA-011 Add traces/tags for node, tool, model, tokens, cost, prompt, embedding, index, corpus, and locale versions.
- [ ] EVA-012 Add private quality dashboard and public summarized methodology/results page.

## 012 — portfolio productization and proof

- [ ] PRT-001 Run `/speckit.specify` for portfolio narrative and public launch proof.
- [ ] PRT-002 Publish README with problem, scope, setup, architecture, limitations, evaluation, cost, latency, and security.
- [ ] PRT-003 Record demo video showing question, evidence, comparison, report, Spanish/English switch, and safe abstention.
- [ ] PRT-004 Publish architecture diagrams and ADRs with trade-offs.
- [ ] PRT-005 Publish technical post explaining retrieval, graph, evidence gate, report pipeline, and failures corrected.
- [ ] PRT-006 Instrument adoption, value, quality, performance, economy, knowledge, and operations KPIs.
- [ ] PRT-007 Publish measurable baseline and post-change comparison; do not use screenshots as sole evidence.
- [ ] PRT-008 Complete external usability, refresh validation, load tests, and security review.
- [ ] PRT-009 Prepare interview narrative showing decisions, failures, metrics, cost controls, and why the architecture is agentic.

