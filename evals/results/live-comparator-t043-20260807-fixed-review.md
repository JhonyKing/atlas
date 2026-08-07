# T043 — Revisión live corregida del comparador

Run: `ed9e093f-74ed-4d47-a5c6-8a05ace0e505`  
Fecha: `2026-08-07`  
Idioma: `es-MX`  
Tecnologías: `langgraph`, `langchain`, `openai`, `anthropic`  
Criterios: `capability`, `tool_calling`, `context`  
Estado terminal: `comparison.completed` / HTTP 200  
Duración: **24,565 ms**

## Propósito

Este documento registra el run posterior a la corrección de T043. El run anterior
`aae76ef0-931b-49bc-9b42-6686f773fcbb` se conserva como evidencia de la regresión original y no fue
sobrescrito.

La corrección distingue observaciones complementarias de contradicciones. Por eso las celdas
`partial` ahora conservan un valor combinado cuando las fuentes agregan hechos compatibles.

## Matriz completa

| Tecnología | Criterio | Estado | Valor mostrado | Evidencias | Veredicto propietario |
|---|---|---|---|---:|---|
| langgraph | capability | partial | Persistence; Checkpointers; Stores; Fault tolerance; Event streaming; Streaming; Interrupts; Time travel | 1 | pending |
| langgraph | tool_calling | partial | LangGraph ejecuta tool calls mediante `state.messages[-1].tool_calls`; puede pausar llamadas para revisión humana; los interrupts dentro de tools permiten aprobar, editar o cancelar | 5 | pending |
| langgraph | context | partial | `context_schema`, dataclass de contexto, objeto `Runtime`, parámetro `context` de `invoke` y acceso desde nodos o conditional edges | 5 | pending |
| langchain | capability | partial | Configuración mediante `model`, `tools` y `system_prompt`; middleware para guardrails, retries, routing y políticas de tools | 2 | pending |
| langchain | tool_calling | partial | Agent loop, selección de tools por el modelo, filesystem/código y streaming de llamadas intermedias | 5 | pending |
| langchain | context | partial | Contexto por ejecución, configuración por usuario/API keys/flags, `context_schema`, ventana de contexto y subagentes aislados | 4 | pending |
| openai | capability | partial | Browser; Computer use; Voice; Plugins; Web search; Image generation; Image inputs; Appshots | 2 | pending |
| openai | tool_calling | partial | Programmatic Tool Calling, `allowed_callers`, `program_items`, preservación de `call_id`, procesamiento de resultados y validación directa | 6 | pending |
| openai | context | unsupported | No comparable value encontrado en la evidencia seleccionada | 0 | expected unsupported |
| anthropic | capability | partial | Claude Fable 5, Claude Mythos 5 y consulta de capacidades/límites mediante Models API | 2 | pending |
| anthropic | tool_calling | partial | Client tools, server tools, `tool_choice`, modo `auto` y parallel tool use | 5 | pending |
| anthropic | context | partial | Context management; Context windows; Compaction; Context editing | 3 | pending |

Las explicaciones de las celdas pobladas son:

> Sources provide multiple qualitative observations without an explicit direct contradiction; the
> comparison preserves each fact.

## Evidencia y asociación

La asociación `ComparisonCell.evidence_ids → Evidence` fue validada mediante el join:

`atlas.chunks → atlas.source_versions → atlas.sources → atlas.collections`

| Validación | Resultado |
|---|---:|
| IDs únicos citados | 40 |
| IDs encontrados en el catálogo | 40 |
| IDs faltantes | 0 |
| Mismatches de colección | 0 |
| Todos los IDs pertenecen a su rama technology/criterion | Sí |
| Estado de mapping | `passed` |

El catálogo fuente conserva `collection`, `title`, `publisher`, `canonical_url`, `source_type`,
`excerpt`, `captured_at` y `version_label`. El registro machine-readable con la matriz completa y
la validación está en
[`live-comparator-t043-20260807-fixed.json`](./live-comparator-t043-20260807-fixed.json).

## Estado de revisión

Este documento queda en `pending_owner_review`. No cierra T040. Para cerrar T040 todavía debe
registrarse el veredicto humano de las 12 celdas de este run nuevo.
