# ATLAS AI — estado de implementación

Este es el tablero rápido del proyecto. El detalle ejecutable vive en cada
`specs/<feature>/tasks.md`; el backlog maestro vive en
`docs/product/prd-v1.1-backlog.md`.

## Estado por feature

| Feature | Tema | Estado | Tareas abiertas en SpecKit | Fuente |
|---|---|---:|---:|---|
| 000 | Foundation y control del producto | No iniciado en SpecKit | — | `docs/product/prd-v1.1-backlog.md` |
| 001 | Respuesta citada y UX bilingüe | Implementación terminada; evidencia humana/temporal pendiente | 4 | `specs/001-cited-answer/tasks.md` |
| 002 | Comparador tecnológico | Cerrada; evidencia live y revisión del owner registradas | 0 | `specs/002-technology-comparator/tasks.md` |
| 003 | Reportes y documentos DOCX/PDF | Cerrada — MVP vertical | 0 | `specs/003-reports/tasks.md` |
| 004 | Auth, sesiones y datos privados | Cerrada — MVP auth y datos privados | 0 | `specs/004-optional-auth-private-data/tasks.md` |
| 005 | Corpus expandido e ingestión gobernada | Cerrada — slice determinista de portafolio | 0 | `specs/005-expanded-curated-corpus/tasks.md` |
| 006 | Grafo de agentes, checkpoints y revisión humana | Cerrada — slice determinista de orquestación y review | 0 | `specs/006-agent-graph-human-review/tasks.md` |
| 007 | Calidad de retrieval y evidencia multilingüe | Cerrada — baseline medido, filtros, diversidad y fallback | 0 | `specs/007-retrieval-quality-multilingual/tasks.md` |
| 008 | Router de modelos, GPT-5.6 Luna y controles de coste | Cerrada — router medido, resiliencia, pricing, budgets, cache y batch eval | 0 | `specs/008-model-router-gpt56-luna/tasks.md` |
| 009 | Seguridad, privacidad y gobernanza | Slice local cerrado; revisión externa documentada como seguimiento | 0 | `specs/009-security-privacy-governance/tasks.md` |
| 010 | Escala, fiabilidad y SLOs | Cerrada — slice determinista de gates y workloads; carga live pendiente | 0 | `specs/010-scale-reliability-slos/tasks.md` |
| 011 | Evaluación, observabilidad y quality loop | Cerrada — evaluadores deterministas, gate y metodología agregada | 0 | `specs/011-evaluation-quality-loop/tasks.md` |
| 012 | Productización y prueba de portafolio | Cerrada — índice, métricas, narrativa y ledger de evidencia | 0 | `specs/012-portfolio-productization-proof/tasks.md` |
| 013 | LangSmith y observabilidad | Cerrado en esta fase | 0 | `specs/013-observability/tasks.md` |
| 014 | Corpus real y harness | En progreso | 1 | `specs/014-real-corpus/tasks.md` |
| 015 | Noticia del día anterior | Cerrado funcionalmente | 0 | `specs/015-daily-news/tasks.md` |
| 016 | Harness conectado a LangSmith | Slice implementado y verificado | 0 | `specs/016-langsmith-evaluation-harness/tasks.md` |

| 017 | CI/CD hardening | Cerrada: workflows hospedados verdes y `main` protegida | 0 | `specs/017-cicd-hardening/tasks.md` |
| 018 | Production deployment | Fundación local implementada: Vercel, contenedor API/worker, readiness, CI, migración y evidencia redacted; activación externa aún pendiente | 6: T031-T036 | `specs/018-production-deployment/tasks.md` |
| 019 | Agent tool orchestration | Planner estructurado GPT-5.6 Luna con fallback determinista, catálogo, plan, aprobación, ejecución bounded, eventos, UI, persistencia Postgres no-development con replay entre repositorios, idempotencia durable, envelopes de evidencia read-only, enlaces de artefactos, trazas de ciclo de vida y evidencia live sin contenido privado | 0 | `specs/019-agent-tool-orchestration/tasks.md` |
| 021 | Migración de base de datos a Supabase | Repositorio y producción alineados en 32 migraciones; `foreign_key_indexes` aplicado y advisors verificados | 0 tareas SpecKit abiertas; el backlog de RLS de las otras tablas requiere un plan separado | `specs/021-supabase-database-migration/tasks.md` |

## Orden recomendado para terminar el MVP de portafolio

1. Activar el runtime administrado de API/worker y sus secretos para cerrar T031–T036 de Feature
   018; esto desbloquea las pruebas reales del producto desplegado.
2. Ejecutar las cuatro evidencias externas de Feature 001: estudio de cinco personas, refresh de
   siete días, quickstart completo y consolidación final.
3. Completar el refresh de siete días de Feature 014. Estas 11 tareas son todo el backlog SpecKit
   actualmente abierto; ninguna es código local pendiente oculto.

## Comandos y archivos que debes consultar

```powershell
# Lista de tareas de una feature
Get-Content specs/003-reports/tasks.md

# Conteo rápido de abiertas/cerradas para una feature existente
$f = 'specs/014-real-corpus/tasks.md'
(Get-Content $f | Select-String '^- \[ \]').Count
(Get-Content $f | Select-String '^- \[X\]').Count
```

El backlog completo mantiene la trazabilidad PRD → feature → tarea:
`docs/product/prd-v1.1-backlog.md`.

## Actualización hospedada (2026-08-11)

La autorización explícita del propietario permitió aplicar `agent_tool_rls` y posteriormente
`foreign_key_indexes` en el proyecto Supabase de producción. El remoto está en 32 migraciones con
`foreign_key_indexes` como head; las siete
tablas durables del agente tienen FORCE RLS, 14 policies worker/read-only y cero grants para
`anon`/`authenticated`. T046 de Feature 021 y T049 de Feature 019 están cerradas; Feature 019 no
tiene tareas SpecKit abiertas. Supabase
todavía reporta 41 tablas `atlas` restantes sin RLS; ese backlog requiere políticas separadas y no
se considera resuelto por esta migración. Evidencia:
`evals/results/supabase-migration-foreign-key-indexes-20260811-applied.json`.

## Evidencia de verificación de Feature 003

- Backend completo: `196 passed, 4 skipped, 3 warnings`.
- Contratos, unitarias e integración de reportes: `13 passed`.
- Migraciones `0016_reports` y `0017_report_metadata` aplicadas en PostgreSQL de Docker Desktop;
  `database/tests/008_reports.sql` pasó.
- Journeys Playwright de generación, DOCX/PDF/eliminación y español: `3 passed`.
- Evaluación determinista bilingüe: `1 passed`.
- PDF renderizado a PNG e inspeccionado visualmente; el validador también exige contenido visible
  en cada página y manifiesto de citas.
