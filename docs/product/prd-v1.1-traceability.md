# ATLAS AI PRD v1.1 — matriz de trazabilidad Spec Kit

**Fuente:** `C:\Users\Usuario\Downloads\Proyecto_ATLAS_AI_PRD_Arquitectura_v1.1.docx`  
**Versión de la fuente:** 1.1 · 30 de julio de 2026  
**Regla:** ningún requisito del PRD se considera entregado sólo porque exista código parecido. Debe
tener una especificación, un plan, tareas, pruebas y evidencia de aceptación.

## Hallazgo de la auditoría

La especificación inicial de `001-cited-answer` fue demasiado estrecha y contradijo la fuente:

- El PRD define el producto como **English-first y bilingüe**, con `en-US` y `es-MX` con paridad
  funcional (tabla “Control del documento”, sección 21 y ADR-007).
- El PRD incluye en el MVP público comparador, reportes DOCX/PDF, perfiles/sesiones, feedback,
  panel de estado, evaluación y experiencia bilingüe (tabla “Incluido”, sección 5.1).
- El PRD exige rutas localizadas `/en` y `/es`, catálogos versionados, `Accept-Language`,
  evidencia original más traducción opcional, renderers EN/ES, 100% de cobertura y paridad de
  citas (tablas de las secciones 8.1 y 21).
- El repositorio decía lo contrario: `T049` hablaba de una página sólo en inglés, el `spec.md`
  declaraba español fuera de alcance y `tasks.md` ordenaba no añadir localización. Eso fue una
  desviación de la fuente y queda corregido por `FR-023`, `FR-024`, `SC-013` y `SC-014`.

## Mapa requisito → artefacto → estado

| ID PRD | Requisito verificable | Sección/fuente | Feature Spec Kit | Estado actual | Evidencia/tarea |
|---|---|---|---|---|---|
| PRD-001 | Producto público de investigación técnica con evidencia | 1–3 | 001 | Parcial | T037–T050; falta completar runtime real |
| PRD-002 | English-first + es-MX con paridad funcional | Control del documento; 21; ADR-007 | 001 | Implementado y probado; falta evidencia operacional real | T078–T084; T086 |
| PRD-003 | Preguntas sobre frameworks/proveedores y cambios de versión | 4–7 | 001 | Parcial | T037–T050; corpus inicial limitado a 3 colecciones |
| PRD-004 | Citas por afirmación, fecha, versión y fuente canónica | 10; 16.2 | 001 | Implementado con fakes | T042–T058; falta smoke real |
| PRD-005 | Comparador configurable de 2–4 tecnologías | 5.1; 7.2; 16.2 | 002 | Parcial: contratos, persistencia, cuota, workflow, UI bilingüe y evaluador implementados; runtime, cuarta colección y baseline de 20 casos pendientes | T001–T041; specs/002-technology-comparator/ |
| PRD-006 | Reportes DOCX/PDF descargables y citados | 1.1; 3.3; 7.2; 16.2 | 003 | No iniciado | Backlog RPT-001–RPT-012 |
| PRD-007 | Architecture brief, ADR, release intelligence, research report | 7.3; tabla de plantillas | 003 | No iniciado | RPT-003–RPT-008 |
| PRD-008 | Auth opcional, sesiones, historial y reportes propios | 5.1; 12.2 | 004 | No iniciado | Backlog IDN-001–IDN-009 |
| PRD-009 | Feedback positivo/negativo y cita incorrecta | 5.1; 14 | 001 | Implementado con fakes | T051–T058 |
| PRD-010 | Panel de fuentes, última actualización y cobertura | 5.1 | 001 / 005 | Parcial | T069; ING-009 |
| PRD-011 | Corpus curado de docs, releases, papers, pricing y uploads autorizados | 6 | 005 | Parcial | T024–T030 sólo cubren 3 colecciones; ING-001–ING-015 |
| PRD-012 | Gobernanza: licencia, robots, hash, takedown, obsolescencia, desactivación | 6.3; 12.3 | 005 | Parcial | T022–T026; ING-012–ING-015 |
| PRD-013 | Router, planner, retrieval, verifier, síntesis, reporte y human review | 7; 9.2 | 006 | Parcial | T039/T044/T062–T065; AGT-001–AGT-010 |
| PRD-014 | Checkpoints persistentes y reanudación para trabajos largos | 9.3 | 006 | No iniciado | AGT-007–AGT-009 |
| PRD-015 | RAG: rewriting, filtros, híbrido, diversidad, reranking y budget | 10.1–10.4 | 007 | Parcial | T037/T042; RET-001–RET-009 |
| PRD-016 | Router de modelos, fallback, costos y GPT-5.6 Luna prioritario | 11; decisión posterior del usuario | 008 | Adapter Luna existe; router no | T019; MOD-001–MOD-010 |
| PRD-017 | Embeddings multilingües y filtros de idioma | tabla 21.2; 10 | 007 / 008 | No iniciado | RET-006; MOD-006 |
| PRD-018 | Secretos, RLS, SSRF, sandbox, uploads, injection, rate limits, auditoría, privacidad | 12.2 | 009 | Parcial | T022/T035/T064; SEC-001–SEC-012 |
| PRD-019 | Escala MVP→beta→100k, colas, cache, HNSW, circuit breakers | 13 | 010 | Parcial | T072; SCL-001–SCL-012 |
| PRD-020 | SLOs: disponibilidad, TTFT, p95, reportes, errores, citas, costo | 13.3 | 010 | Parcial | T072; SCL-004–SCL-008 |
| PRD-021 | Golden dataset: factual, temporal, comparación, abstención, injection, reportes, bilingüe | 14.2 | 011 | Parcial | T070/T071; EVA-001–EVA-006 |
| PRD-022 | Evals offline/online, gates de regresión, trazas y dashboard | 14.1–14.4 | 011 / 013 / 016 | Parcial; offline, dry-run, smoke real y un answer trace verificados; evaluación completa pendiente | T070–T073; EVA-007–EVA-012; T015 |
| PRD-023 | Roadmap verificable de 12 semanas | 15 | 000 | Documentado | RDM-001–RDM-012 |
| PRD-024 | Repo modular: web, API, worker, agent, retrieval, ingestion, models, reports, evaluation | 17 | 000 | Adaptado a monorepo actual | RDM-013 |
| PRD-025 | ADRs, README, demo, video, post técnico y narrativa de entrevista | 18–20; ADR-001–ADR-009 | 012 | Parcial | T073/T077; PRT-001–PRT-009 |
| PRD-026 | KPIs de adopción, valor, calidad, rendimiento, economía, conocimiento y operación | apéndice KPI | 012 | No iniciado | PRT-006–PRT-008 |
| PRD-027 | SDD con Spec Kit: specify → clarify → plan → tasks → analyze → tests → implement → converge | 22; tabla de gates | Todas | En uso | Esta matriz y los feature folders |

## Addendum del Plan Maestro RAG/Evals

La auditoría de `PLAN-MAESTRO-RAG-EVALS.docx` no reemplaza esta matriz. Añade tres superficies que
deben quedar trazadas antes de declarar el producto listo:

| Necesidad agregada | Requisito PRD relacionado | Feature Spec Kit | Tareas nuevas |
|---|---|---|---|
| Observabilidad LangSmith de trazas, feedback y evaluaciones | PRD-018, PRD-022, PRD-026 | 013 | PM-001–PM-008, OBS-001–OBS-015, EVA-017–EVA-020 |
| Corpus real de múltiples documentos/páginas, OCR y harness separado | PRD-002, PRD-011, PRD-012, PRD-015, PRD-021 | 014 | COR-001–COR-014, EVA-013–EVA-016 |
| Noticia verificable del día anterior | PRD-001, PRD-004, PRD-005, PRD-011, PRD-022 | 015 | NEWS-001–NEWS-012 |

El conteo actualizado del backlog maestro es **192 tareas totales: 156 abiertas y 36 marcadas como
completadas**. El vertical slice `specs/001-cited-answer/tasks.md` mantiene **88 tareas: 5 abiertas y
83 completadas**; las cuatro nuevas tareas T085–T088 provienen de la convergencia del 2026-08-05.
Estas cifras no deben sumarse porque representan niveles distintos de planificación.

## Evidencia de cierre parcial de features 013–014

- **013 Observabilidad:** siete pruebas de observabilidad pasaron; el dry-run de LangSmith no hizo
  llamadas de red; el harness offline `rag-v1` pasó sus 60 casos; el smoke real y un answer trace
  fueron verificados en el proyecto `atlas-ai`, con runs `atlas.answer`, `atlas.retrieval`,
  `atlas.generation` y `atlas.verification` en estado exitoso. La evaluación completa de 60 casos
  permanece opt-in por su posible coste.
- **014 Corpus real:** el runtime de producción exige un snapshot verificado y el fallback demo
  queda limitado a desarrollo; la integración de producción pasó contra el snapshot local activo.

## Evidencia de avance del feature 002

- **Foundation y contratos:** `T001–T011` pasaron pruebas de esquemas, migraciones PostgreSQL,
  cuota separada de cinco comparaciones, fan-out de retrieval y restricciones por rama.
- **P1:** `T012–T023` pasaron contratos API/SSE, persistencia, normalización, workflow, cliente
  tipado, UI accesible y journey Playwright de dos tecnologías.
- **Seguridad y estados:** `T024–T029` pasaron el evidence gate, fixture de prompt injection,
  restricciones temporales/versiones y UI de estados unsupported/partial/contradictory.
- **Bilingüe y observabilidad:** `T030–T031` y `T034` pasaron paridad Chromium, catálogos EN/ES
  y pruebas de metadata segura para LangSmith; `T035–T036` pasaron el evaluador determinista y
  las puertas locales (168 backend tests, 11 Playwright).
- **Pendiente explícito:** `T032–T033` y `T039` requieren una cuarta colección aprobada; `T038`
  debe conectar el ejecutor real de retrieval/workflow (el coordinador fail-closed y la traza
  LangSmith ya están cableados);
  `T040` debe ampliar el baseline a 20
  solicitudes y medir latencia/calidad; `T041` depende de resolver el runner Vitest de Windows.

## Regla de entrega

`001-cited-answer` es el primer vertical slice, no el PRD completo. No se puede cerrar el producto
como “listo” hasta que los features 002–012 tengan sus propios `spec.md`, `plan.md`, `tasks.md`,
pruebas y resultados. El backlog siguiente es la lista maestra que evita que las expansiones del
PRD desaparezcan detrás de la palabra “futuro”.
