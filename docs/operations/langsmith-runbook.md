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
otra. El SDK conserva visibles los inputs/outputs ya sanitizados. Para evaluar el flujo de respuesta,
las trazas `atlas.answer`, `atlas.retrieval`, `atlas.generation` y `atlas.verification` incluyen la
pregunta, evidencia recuperada, respuesta generada y resultado de verificación. El sanitizador
recursivo redacta claves y valores con forma de credencial, limita strings a 4.000 caracteres,
secuencias a 20 elementos, objetos a 50 campos y la profundidad a seis niveles.

## Verificación

1. Ejecuta la suite offline; debe pasar incluso sin estas variables.
2. Con una key de prueba, activa el smoke test opt-in y busca el proyecto `atlas-ai`.
3. Confirma que el trace contiene `atlas.answer`, `atlas.retrieval`, `atlas.generation` y
   `atlas.verification`; comprueba que pregunta, evidencia, respuesta y verificación sean visibles,
   y que cookies, cabeceras de autorización, API keys, tokens, contraseñas y secretos aparezcan
   redactados o no aparezcan.
4. Si LangSmith no responde, conserva el run local OpenTelemetry y revisa el error por request ID;
   la respuesta de usuario no debe fallar por una caída de observabilidad.

## Privacidad y mantenimiento

- Respeta los 30 días de retención de contenido anónimo definidos por el PRD y limita el acceso al
  proyecto de producción a operadores autorizados, porque las trazas contienen contenido funcional.
- Revisa cualquier nuevo payload antes de añadirlo. Pregunta, evidencia, respuesta y verificación
  están autorizadas para evaluación; nunca agregues `authorization`, `cookie`, API keys, tokens,
  contraseñas, credenciales o secretos.
- Rota las claves con caducidad y elimina las claves antiguas desde LangSmith.
- Guarda en el repositorio sólo nombres de proyecto, versiones, resultados agregados y esta guía.

## Retención, borrado y rotación

Antes de borrar o retener datos, confirma el proyecto, el intervalo UTC y el
motivo en el registro operativo. El procedimiento mínimo es:

1. Exporta sólo agregados necesarios para el informe; no exportes inputs/outputs fuera del workspace
   de evaluación autorizado.
2. Aplica la política de 30 días del PRD a contenido anónimo y conserva únicamente
   identificadores/versiones necesarios para auditoría.
3. Ejecuta la eliminación en el workspace correcto y verifica que el conteo
   posterior coincide con el intervalo solicitado.
4. Revoca la clave anterior, crea la nueva en el gestor de secretos, actualiza
   el despliegue y ejecuta el smoke test opt-in.
5. Confirma que el fallback no-op mantiene la API disponible si el proveedor
   externo no responde.

Lista de comprobación de redacción: `authorization`, `cookie`, API keys, tokens, contraseñas,
credenciales y secretos no deben aparecer sin redactar. Pregunta, evidencia, respuesta y verificación
sí aparecen en las trazas de respuesta para permitir su evaluación.
