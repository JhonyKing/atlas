# Auditoría aditiva del Plan Maestro RAG/Evals

**Fuente revisada:** `C:\Users\Usuario\Desktop\PLAN-MAESTRO-RAG-EVALS.docx`  
**Fuente de autoridad de producto:** `C:\Users\Usuario\Downloads\Proyecto_ATLAS_AI_PRD_Arquitectura_v1.1.docx`  
**Fecha de revisión:** 2026-08-05

## Regla de precedencia

El PRD v1.1 sigue siendo la fuente de autoridad. El Plan Maestro agrega diseño operativo para
evaluación, observabilidad y corpus, pero no puede eliminar ni reducir una capacidad del PRD. Las
decisiones del Plan Maestro que contradigan al PRD se conservan como historial y se convierten en
una tarea de reconciliación; no se aplican como sustitución silenciosa.

## Hallazgo principal

El Plan Maestro describe un sistema histórico con 12 PDFs reales y 1,038 chunks, un harness
separado de evaluación y un proyecto de LangSmith llamado `RAGwithPDFSv2`. Esas cifras y ese
proyecto **no están verificadas en el repositorio ATLAS actual**. El repositorio actual sí contiene
la arquitectura de ingestión versionada, PostgreSQL/pgvector, OpenTelemetry y tres colecciones
canónicas, pero el runtime de desarrollo todavía usa evidencia demo determinista cuando no hay un
snapshot de corpus real. Por lo tanto, no se presenta el corpus actual como real hasta ejecutar una
ingesta reproducible y verificar sus fuentes, hashes, fechas y conteo de páginas/chunks.

## Matriz Plan Maestro → Spec Kit

| Área del Plan Maestro | Evidencia en ATLAS | Estado | Artefacto/tareas aditivas |
|---|---|---|---|
| LangSmith desde el primer día | OpenTelemetry y logs sin contenido; no hay cliente LangSmith configurado en `pyproject.toml` | Parcial | `specs/013-observability/`; OBS-001–OBS-015 |
| Ciclo prototipo → beta → producción | No hay dataset de trazas, cola de anotación ni runbook de promoción | Pendiente | EVA-013–EVA-020, OBS-008–OBS-015 |
| Harness separado de evals | Existe `atlas-eval`, pero falta dataset versionado de ~60 casos y ejecución HTTP reproducible | Parcial | EVA-013–EVA-020 |
| Métricas RAG modernas | Hay base de evaluación, pero faltan Hit@k, MRR, precisión/recall de contexto, reranking y freshness | Parcial | EVA-014–EVA-018, COR-010–COR-012 |
| Corpus de 12 PDFs/1,038 chunks | El repositorio actual no contiene esos PDFs ni un snapshot verificable | No verificado | `specs/014-real-corpus/`; COR-001–COR-014 |
| Noticia más importante del día anterior | No existe modelo, ingesta, ranking, endpoint ni UI | Pendiente | `specs/015-daily-news/`; NEWS-001–NEWS-012 |
| Modernización | El proyecto actual usa Pydantic 2 y LangGraph; no se hará downgrade a LangServe ni a variables legacy | Resuelto por decisión | PM-001–PM-008 |

## Decisiones de implementación

1. Se conserva el runtime demo, porque permite pruebas deterministas y una experiencia local sin
   proveedor. Se añade una ruta de corpus real y el runtime sólo la publicará como `READY` después
   de contar con un snapshot válido.
2. LangSmith será una integración opcional y segura: `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`,
   `LANGSMITH_PROJECT` y, si aplica, `LANGSMITH_ENDPOINT`/`LANGSMITH_WORKSPACE_ID`. Las pruebas no
   dependerán de red ni contendrán claves. Los inputs/outputs completos no se enviarán por defecto;
   los trazos usarán hashes, IDs, tamaños, latencias, tokens, coste y versiones.
3. La noticia diaria no se inventará ni se elegirá por una sola señal. Se definirá una ventana
   temporal explícita (día calendario UTC anterior), fuentes RSS/Atom permitidas, ranking auditable,
   deduplicación y una salida `unavailable` cuando no exista evidencia suficiente.
4. El corpus ampliado almacenará metadatos y extractos acotados, no copias completas de artículos.
   Cada fuente tendrá URL canónica, publisher, fecha de captura, hash, licencia/robots y versión.

## Criterio de cierre de esta auditoría

La auditoría queda cubierta cuando cada fila anterior tiene `spec.md`, `plan.md`, `tasks.md`, una
prueba automatizada o un resultado de evaluación, y una evidencia de ejecución. El número de tareas
del backlog maestro se calcula con las casillas de este archivo; las tareas `Txxx` de cada feature
se cuentan por separado.

