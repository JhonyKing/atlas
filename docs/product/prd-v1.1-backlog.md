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

- [X] CMP-001 Run `/speckit.specify` for configurable 2–4 technology comparison with explicit criteria and evidence per cell.
- [X] CMP-002 Specify supported criteria: capability, tool calling, context, latency, price, license, freshness, and operational risk.
- [X] CMP-003 Plan comparison state, retrieval fan-out, normalization, missing-value semantics, and contradiction handling.
- [X] CMP-004 Write contract, domain, retrieval, and accessible UI tests before implementation. (Spec Kit T004, T010, T012–T014, T022–T023.)
- [X] CMP-005 Implement comparison request and asynchronous progress flow. (Spec Kit T012–T020; runtime wiring remains a convergence task.)
- [X] CMP-006 Implement evidence-backed comparison matrix and claim-level citations for every populated cell. (Spec Kit T014–T019, T024–T025.)
- [X] CMP-007 Implement criterion selection, source/date/version filters, and unsupported-cell explanation. (Spec Kit T016–T017, T022, T028–T029.)
- [ ] CMP-008 Add deterministic dataset cases for two-, three-, and four-technology comparisons. (Two, three and a four-row Anthropic case are present; verified fourth corpus remains pending T032/T039.)
- [X] CMP-009 Add Playwright journey and regression gate; prove the comparator is not a generic chat response. (Spec Kit T023, T029, T036.)

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

- [X] ING-001 Run `/speckit.specify` for expanded sources while preserving the allowlist boundary.
- [X] ING-002 Add connector specs for 10–15 frameworks and 6–8 model providers.
- [X] ING-003 Add GitHub Releases/changelog connector with 6–24 hour schedule.
- [X] ING-004 Add OpenAlex/Semantic Scholar metadata connector and paper links.
- [X] ING-005 Add official pricing/model-list snapshots with change detection.
- [X] ING-006 Add authorized user-content connector with private tenant storage.
- [X] ING-007 Implement sitemap/API/versioned-page discovery and bounded fetch policies.
- [X] ING-008 Implement HTML/Markdown/PDF normalization that preserves headings, tables, and code blocks.
- [X] ING-009 Implement source panel coverage/freshness/disabled-state reporting.
- [X] ING-010 Implement metadata: canonical URL, title, author/org, published/captured dates, license, hash.
- [X] ING-011 Implement version relation, staleness/TTL, and historical-vs-current classification.
- [X] ING-012 Implement robots/ToS/license review gates and source enablement approval.
- [X] ING-013 Implement takedown/correction workflow and atomic source disablement.
- [X] ING-014 Add per-collection retry, dead-letter, preservation, and re-review trigger tests.
- [X] ING-015 Validate the full refresh and coverage dashboard against the seven-day operational target.

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

- [X] RET-001 Run `/speckit.specify` for production retrieval quality beyond the exact hybrid baseline.
- [X] RET-002 Implement query rewriting for terms, versions, aliases, and synonyms.
- [X] RET-003 Implement filters for provider, framework, date, version, language, and source type.
- [X] RET-004 Implement MMR/deduplication diversity and parent-child context windows.
- [X] RET-005 Implement measured reranking/cross-encoder behind an adapter, only after baseline comparison.
- [X] RET-006 Benchmark multilingual embeddings and language-aware retrieval.
- [X] RET-007 Implement evidence-budget token limits and authority/freshness prioritization.
- [X] RET-008 Add Hit@5, MRR, context precision/recall, citation precision, and freshness accuracy evals.
- [X] RET-009 Add temporal, cross-language, contradiction, and source-version regression cases.

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

## 013 — Plan Maestro: LangSmith y observabilidad de calidad

Estas tareas agregan lo descrito en `PLAN-MAESTRO-RAG-EVALS.docx` sin retirar la telemetría
OpenTelemetry ya implementada. Deben pasar por `specs/013-observability/` antes de considerarse
implementadas.

- [X] PM-001 Reconciliar las decisiones históricas del Plan Maestro con el PRD v1.1 y registrar qué no se puede verificar en el repositorio actual.
- [ ] PM-002 Mantener Pydantic 2, LangGraph y la Responses API como línea moderna; documentar por qué no se migra hacia atrás a LangServe ni a variables LangChain legacy.
- [X] PM-003 Versionar los nombres de proyecto, dataset, prompt, retriever, embedding, índice y corpus usados por cada experimento.
- [X] PM-004 Definir la política de privacidad de trazas: contenido completo desactivado por defecto, hashes/IDs como correlación y retención alineada al PRD.
- [ ] PM-005 Definir el contrato de promoción prototipo → beta → producción con criterios observables y reversibles.
- [X] PM-006 Añadir un runbook de diagnóstico que empiece por request ID, run ID y versión de corpus, sin imprimir secretos ni contenido de usuario.
- [ ] PM-007 Registrar el coste y el estado de las integraciones externas como evidencia, no como afirmación de que están activas.
- [ ] PM-008 Ejecutar `/speckit.analyze` y `/speckit.converge` después de cada fase de esta expansión.

- [X] OBS-001 Ejecutar `/speckit.specify` para trazabilidad LangSmith de extremo a extremo.
- [X] OBS-002 Planificar una interfaz de tracing desacoplada del SDK para conservar pruebas offline y permitir fallback no-op.
- [X] OBS-003 Configurar `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` y endpoint/workspace opcionales sólo desde secretos locales o del despliegue.
- [ ] OBS-004 Instrumentar request, retrieval, generación, verificación, feedback y streaming con un árbol de runs correlacionado.
- [ ] OBS-005 Propagar `X-Request-ID`, `X-Atlas-Run-ID`, locale, modelo, prompt version, retrieval version y snapshot ID como metadata segura.
- [ ] OBS-006 Etiquetar cada run por entorno, colección, tipo de pregunta, resultado (`complete`, `partial`, `abstained`, `failed`) y versión de aplicación.
- [ ] OBS-007 Registrar tokens, coste estimado, latencia, TTFT, retries, fallback y error code sin enviar preguntas ni excerpts completos por defecto.
- [X] OBS-008 Añadir pruebas unitarias con cliente LangSmith falso y pruebas contractuales que confirmen que una clave ausente no rompe la API.
- [X] OBS-009 Añadir smoke test opt-in contra LangSmith que verifique creación de un trace y lo marque como prueba, sin incluir secretos en logs.
- [ ] OBS-010 Conectar feedback negativo e “incorrect citation” a una cola de revisión y a un dataset de casos difíciles.
- [X] OBS-011 Definir datasets de evaluación versionados y el enlace entre dataset, experimento, trace y commit.
- [X] OBS-012 Crear dashboards privados de latencia, coste, error, abstención, citas y feedback segmentados por locale, colección y versión.
- [ ] OBS-013 Añadir comparación A/B de prompts, retrievers y modelos con tags reproducibles y criterio de promoción.
- [X] OBS-014 Documentar retención, borrado de trazas y procedimiento de redacción/rotación de claves.
- [ ] OBS-015 Publicar evidencia de observabilidad para el portafolio: diagrama, captura sin PII, métricas y limitaciones verificadas.

## 014 — Corpus real ampliado y harness de evaluación

- [X] COR-001 Ejecutar `/speckit.specify` para el corpus real ampliado y su refresh reproducible.
- [X] COR-002 Definir un manifiesto versionado de fuentes oficiales para LangGraph, LangChain y OpenAI con URL canónica, tipo, publisher y licencia/robots.
- [ ] COR-003 Ampliar el manifiesto a un mínimo verificable de 12 documentos/fuentes y más de tres páginas por colección; registrar páginas, bytes, hash y chunks resultantes.
- [X] COR-004 Implementar el bootstrap reproducible que descarga, normaliza, chunkifica, embebe y promueve un snapshot atómico.
- [ ] COR-005 Mantener el comportamiento append-only: una descarga fallida no reemplaza la versión activa y un contenido idéntico no duplica chunks.
- [ ] COR-006 Añadir validación de tipo, tamaño, redirecciones, SSRF, robots/licencia y dominio permitido antes de persistir una fuente.
- [ ] COR-007 Incorporar OCR spa+eng para PDFs autorizados y guardar idioma, confianza y página de origen de cada chunk.
- [ ] COR-008 Verificar que el runtime cambia de demo a snapshot real sólo cuando el snapshot está completo y activo.
- [X] COR-009 Exponer en el panel el conteo de fuentes, páginas, chunks, última captura, versión y estado de cada colección.
- [X] COR-010 Construir un dataset de aproximadamente 60 preguntas: factual, multi-hop, OCR, bilingüe y no-answer, con ground truth de chunk IDs.
- [X] COR-011 Separar el entorno `evals/` del entorno de producción y ejecutar las evaluaciones contra HTTP de forma reproducible.
- [X] COR-012 Implementar faithfulness, context precision/recall, Hit@k, MRR, citation precision y freshness con resultados versionados.
- [ ] COR-013 Evaluar k=4/8/10, BM25+híbrido, reranking y prompt anti-alucinación mediante tabla de ablación reproducible.
- [ ] COR-014 Publicar el corpus y harness con límites, procedencia, costes, fallos conocidos y resultado de la validación de siete días.

## 015 — Noticia principal del día anterior

- [X] NEWS-001 Ejecutar `/speckit.specify` para la sección de noticia diaria con evidencia y atribución.
- [X] NEWS-002 Definir “día anterior” como ventana de calendario UTC cerrada y mostrar timezone/fecha en la UI.
- [X] NEWS-003 Crear una allowlist versionada de feeds RSS/Atom y páginas públicas con publisher, licencia y política de robots.
- [X] NEWS-004 Implementar fetch con timeout, límites de tamaño, redirecciones seguras, validación de fecha y deduplicación por URL/hash.
- [X] NEWS-005 Normalizar título, resumen acotado, publisher, autor, URL canónica, fecha de publicación y fecha de captura sin almacenar el artículo completo.
- [X] NEWS-006 Definir ranking auditable de importancia usando recencia, autoridad, cobertura independiente y relevancia temática; no afirmar “más importante” sin señales suficientes.
- [X] NEWS-007 Implementar salida `unavailable` cuando no haya una noticia verificable de la ventana, en vez de inventar o rellenar con noticias antiguas.
- [X] NEWS-008 Añadir endpoint y contrato OpenAPI para obtener la noticia diaria con estado, fecha, fuente y citas.
- [X] NEWS-009 Añadir componente bilingüe `/en` y `/es` que traduzca la interfaz pero conserve título/extracto original etiquetado y URL de la fuente.
- [X] NEWS-010 Añadir tests de ventana temporal, timezone, duplicados, feed caído, contenido malicioso y ausencia de evidencia.
- [ ] NEWS-011 Añadir tracing y métricas de freshness, cobertura de feeds, latencia, errores y ranking sin PII.
- [ ] NEWS-012 Documentar límites editoriales, derechos de autor, correcciones/takedown y evidencia de una ejecución real.

## 016 — Harness de evaluación conectado a LangSmith

- [X] EVA-013 Crear el dataset inicial de ~60 ejemplos con inputs, referencia, chunk IDs, idioma, tipo de pregunta y versión de corpus.
- [ ] EVA-014 Implementar graders deterministas para esquema, citas, enlaces, abstención, duplicados y estructura de reportes.
- [ ] EVA-015 Implementar graders de código/modelo/humano con salida estructurada de fortalezas, debilidades, razonamiento y score.
- [X] EVA-016 Ejecutar evaluaciones offline sin API externa y guardar JSON/CSV reproducible con commit y configuración.
- [X] EVA-017 Ejecutar evaluación online opt-in en LangSmith enlazando dataset, experimento, traces y feedback.
- [ ] EVA-018 Exportar casos negativos anotados a un dataset de regresión sin copiar secretos ni PII.
- [ ] EVA-019 Añadir gate CI que bloquee regresiones de citas, faithfulness, abstención, coste o latencia según umbrales versionados.
- [ ] EVA-020 Publicar tabla baseline/ablación/post-cambio con metodología y limitaciones, nunca sólo capturas de pantalla.
