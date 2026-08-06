# ATLAS AI — estado de implementación

Este es el tablero rápido del proyecto. El detalle ejecutable vive en cada
`specs/<feature>/tasks.md`; el backlog maestro vive en
`docs/product/prd-v1.1-backlog.md`.

## Estado por feature

| Feature | Tema | Estado | Tareas abiertas en SpecKit | Fuente |
|---|---|---:|---:|---|
| 000 | Foundation y control del producto | No iniciado en SpecKit | — | `docs/product/prd-v1.1-backlog.md` |
| 001 | Respuesta citada y UX bilingüe | En progreso | 5 | `specs/001-cited-answer/tasks.md` |
| 002 | Comparador tecnológico | En progreso/evidencia live | 4 | `specs/002-technology-comparator/tasks.md` |
| 003 | Reportes y documentos DOCX/PDF | MVP vertical en progreso | 46 | `specs/003-reports/tasks.md` |
| 004 | Auth, sesiones y datos privados | No iniciado | — | `docs/product/prd-v1.1-backlog.md` |
| 005–012 | Corpus expandido, agentes, retrieval, router, seguridad, SLOs, evals y productización | No iniciado | — | `docs/product/prd-v1.1-backlog.md` |
| 013 | LangSmith y observabilidad | Cerrado en esta fase | 0 | `specs/013-observability/tasks.md` |
| 014 | Corpus real y harness | En progreso | 1 | `specs/014-real-corpus/tasks.md` |
| 015 | Noticia del día anterior | Cerrado funcionalmente | 0 | `specs/015-daily-news/tasks.md` |
| 016 | Harness conectado a LangSmith | Pendiente de especificar | — | `docs/product/prd-v1.1-backlog.md` |

| 017 | CI/CD hardening | Slice implementado | 0 | `specs/017-cicd-hardening/tasks.md` |

## Orden recomendado para terminar el MVP de portafolio

1. Cerrar las evidencias pendientes de 001, 002 y 014: quickstart, refresh de siete días,
   usabilidad externa y revisión de las casillas de convergencia.
2. Implementar feature 003: generación de reportes DOCX/PDF con citas, descarga y expiración.
3. Crear el SpecKit de feature 016 y conectar el harness a LangSmith con métricas reproducibles.
4. Ejecutar el corte de portfolio en feature 012: README, arquitectura, costes, latencia,
   seguridad, demo y tabla de evaluaciones.
5. Después ampliar features 004–011 según el trabajo objetivo; no son necesarias para el primer
   MVP demostrable, pero sí forman parte del PRD completo.

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
