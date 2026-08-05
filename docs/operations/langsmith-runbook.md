# LangSmith runbook de ATLAS

## Activación local

Configura estas variables únicamente en `.env.local` o en el gestor de secretos del despliegue:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<secret>
LANGSMITH_PROJECT=atlas-ai
# Opcional: LANGSMITH_ENDPOINT, LANGSMITH_WORKSPACE_ID
```

La configuración oficial actual usa `LANGSMITH_TRACING` y `LANGSMITH_API_KEY`; no se deben añadir
claves a `.env.example`, al frontend, a commits ni a logs. Si la API key se expone, revócala y crea
otra. El SDK se inicializa con captura de inputs/outputs ocultos; los trazos de ATLAS envían sólo
IDs, versiones, tamaños, contadores, estados, latencias y clases de coste.

## Verificación

1. Ejecuta la suite offline; debe pasar incluso sin estas variables.
2. Con una key de prueba, activa el smoke test opt-in y busca el proyecto `atlas-ai`.
3. Confirma que el trace contiene `atlas.answer`, `atlas.retrieval`, `atlas.generation` y
   `atlas.verification`, y que no contiene la pregunta, el answer, excerpts, cookies ni secretos.
4. Si LangSmith no responde, conserva el run local OpenTelemetry y revisa el error por request ID;
   la respuesta de usuario no debe fallar por una caída de observabilidad.

## Privacidad y mantenimiento

- Respeta los 30 días de retención de contenido anónimo definidos por el PRD.
- Revisa tags y metadata antes de añadir nuevos campos; nunca agregues `question`, `prompt`,
  `evidence`, `excerpt`, `authorization`, `cookie` o valores `secret`.
- Rota las claves con caducidad y elimina las claves antiguas desde LangSmith.
- Guarda en el repositorio sólo nombres de proyecto, versiones, resultados agregados y esta guía.

## Retención, borrado y rotación

Antes de borrar o retener datos, confirma el proyecto, el intervalo UTC y el
motivo en el registro operativo. El procedimiento mínimo es:

1. Exporta sólo agregados necesarios para el informe; no exportes inputs/outputs.
2. Aplica la política de 30 días del PRD a contenido anónimo y conserva únicamente
   identificadores/versiones necesarios para auditoría.
3. Ejecuta la eliminación en el workspace correcto y verifica que el conteo
   posterior coincide con el intervalo solicitado.
4. Revoca la clave anterior, crea la nueva en el gestor de secretos, actualiza
   el despliegue y ejecuta el smoke test opt-in.
5. Confirma que el fallback no-op mantiene la API disponible si el proveedor
   externo no responde.

Lista de comprobación de redacción: `question`, `answer`, `prompt`, `evidence`,
`excerpt`, `authorization`, `cookie`, API keys, tokens, emails y comentarios de
usuario no deben aparecer en trazas externas por defecto.
