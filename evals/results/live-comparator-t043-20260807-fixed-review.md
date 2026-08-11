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

## Evidence catalog

Esta tabla contiene las 40 evidencias realmente asociadas al run. Los excerpts son los fragmentos
acotados almacenados por ATLAS y los enlaces canónicos permiten abrir la fuente original.

| Full evidence ID | Collection / technology | Title | Publisher | Canonical URL | Source type | Bounded excerpt | Captured at | Version label |
|---|---|---|---|---|---|---|---|---|
| `b744c1a8-f160-4aa4-94b9-059d2a9fe19c` | langgraph | LangGraph overview | LangChain | https://docs.langchain.com/oss/python/langgraph/overview | documentation | ### Capabilities<br><br>Persistence<br><br>Checkpointers<br><br>Stores<br><br>Fault tolerance<br><br>Event streaming<br><br>Streaming<br><br>Interrupts<br><br>Time travel<br><br>Memory<br><br>Subgraphs | 2026-08-05T19:34:28.288173+00:00 | — |
| `a2327062-ce0f-4bc0-96aa-7a485a90fa7c` | langgraph | LangGraph interrupts | LangChain | https://docs.langchain.com/oss/python/langgraph/interrupts | documentation | def tool_node(state: AgentState):<br>    """Performs the tool call"""<br>    result = []<br>    for tool_call in state["messages"][-1].tool_calls:<br>        tool = tools_by_name[tool_call["name"]]<br>        observation = tool.invoke(tool_call["args"])<br>        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))<br>    return {"messages": result} | 2026-08-05T19:35:04.945016+00:00 | — |
| `de93d415-f10d-4baf-889c-256352dbd89a` | langgraph | LangGraph interrupts | LangChain | https://docs.langchain.com/oss/python/langgraph/interrupts | documentation | Interrupting tool calls: Pause before executing tool calls to review and edit the tool call before execution | 2026-08-05T19:35:04.945016+00:00 | — |
| `ddc2bcc6-ee86-499d-8df7-8b8ee00c9437` | langgraph | LangGraph interrupts | LangChain | https://docs.langchain.com/oss/python/langgraph/interrupts | documentation | Review and edit: Let humans review and modify LLM outputs or tool calls before continuing | 2026-08-05T19:35:04.945016+00:00 | — |
| `cc393329-4066-4449-a62f-fed9c1a072ff` | langgraph | LangGraph interrupts | LangChain | https://docs.langchain.com/oss/python/langgraph/interrupts | documentation | You can also place interrupts directly inside tool functions. This makes the tool itself pause for approval whenever it’s called, and allows for human review and editing of the tool call before it is executed.<br>First, define a tool that uses interrupt: | 2026-08-05T19:35:04.945016+00:00 | — |
| `e9c05c2d-44e3-44a7-9fc8-fc6dfe440a63` | langgraph | LangGraph interrupts | LangChain | https://docs.langchain.com/oss/python/langgraph/interrupts | documentation | This approach is useful when you want the approval logic to live with the tool itself, making it reusable across different parts of your graph. The LLM can call the tool naturally, and the interrupt will pause execution whenever the tool is invoked, allowing you to approve, edit, or cancel the action. | 2026-08-05T19:35:04.945016+00:00 | — |
| `0813c640-f7fd-4519-b31e-fef52334a8de` | langgraph | LangGraph graph API | LangChain | https://docs.langchain.com/oss/python/langgraph/graph-api | documentation | When creating a graph, you can specify a context_schema for runtime context passed to nodes. This is useful for passing<br>information to nodes that is not part of the graph state. For example, you might want to pass dependencies such as model name or a database connection. | 2026-08-05T19:34:36.046236+00:00 | — |
| `8e145d01-8785-424b-90f0-806bc6ff488c` | langgraph | LangGraph graph API | LangChain | https://docs.langchain.com/oss/python/langgraph/graph-api | documentation | @dataclass<br>class Context:<br>    user_id: str | 2026-08-05T19:34:36.046236+00:00 | — |
| `6db34524-def9-4d88-ae87-e806bc50bf8e` | langgraph | LangGraph graph API | LangChain | https://docs.langchain.com/oss/python/langgraph/graph-api | documentation | runtime—A Runtime object that contains runtime context and other information like store, stream_writer, execution_info, server_info, heartbeat (for idle timeout refresh), and control (for graceful shutdown) | 2026-08-05T19:34:36.046236+00:00 | — |
| `f78a02b9-01e7-42e8-bcf4-4b1a3e69abf0` | langgraph | LangGraph graph API | LangChain | https://docs.langchain.com/oss/python/langgraph/graph-api | documentation | You can then pass this context into the graph using the context parameter of the invoke method. | 2026-08-05T19:34:36.046236+00:00 | — |
| `ca20f892-db5e-43f8-93be-c227904097d8` | langgraph | LangGraph graph API | LangChain | https://docs.langchain.com/oss/python/langgraph/graph-api | documentation | You can then access and use this context inside a node or conditional edge: | 2026-08-05T19:34:36.046236+00:00 | — |
| `e29508eb-52d9-4d86-b5a5-bf6f24d58890` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | Building on that, you can configure the basics directly with the model=, tools=, and system_prompt= parameters. For more advanced capabilities, extend the harness with middleware. | 2026-08-05T19:39:31.311323+00:00 | — |
| `f450f5a6-1445-41c7-9a90-076e584c0e2b` | langchain | LangChain overview | LangChain | https://docs.langchain.com/oss/python/langchain/overview | documentation | ## Highly configurable harness<br><br>Start with create_agent as a minimal harness and add capabilities incrementally through middleware. Compose only what your use case needs, from guardrails and retries to routing and custom tool policies.<br><br>Learn more | 2026-08-05T19:35:21.019153+00:00 | — |
| `3744fd33-4c6b-445f-9ccc-60bf76311ed8` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | An agent is a model calling tools in a loop until a given task is complete. | 2026-08-05T19:39:31.311323+00:00 | — |
| `48fa7485-b21d-4855-b787-b8939e77e992` | langchain | LangChain middleware | LangChain | https://docs.langchain.com/oss/python/langchain/middleware/overview | documentation | The core agent loop involves calling a model, letting it choose tools to execute, and then finishing when it calls no more tools: | 2026-08-05T19:40:01.534270+00:00 | — |
| `eb377e82-0e4f-454f-a337-06107049c779` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | Agents are especially useful when they can take action rather than just generate text. The execution environment gives the agent a workspace: tools it can call, a filesystem for reading and writing files across turns, and code execution for running scripts or shell commands. | 2026-08-05T19:39:31.311323+00:00 | — |
| `aeba1335-2c93-43dd-aa19-b9b5ad96c0c8` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | stream = agent.stream_events(<br>    {"messages": [{"role": "user", "content": "Search for AI news and summarize the findings"}]},<br>    version="v3",<br>)<br>for snapshot in stream.values:<br>    # Each snapshot contains the full state at that point<br>    latest_message = snapshot["messages"][-1]<br>    if latest_message.content:<br>        if isinstance(latest_message, HumanMessage):<br>            print(f"User: {latest_message.content}")<br>        elif isinstance(latest_message, AIMessage):<br>            print(f"Agent: {latest_message.content}")<br>    elif latest_message.tool_calls:<br>        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}") | 2026-08-05T19:39:31.311323+00:00 | — |
| `32fd5e1e-255f-432c-8705-f660f9e38600` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | invoke returns the final response at the end of a run. If an agent executes multiple tool calls, users often need progress updates before completion. Use streaming to surface intermediate messages and tool activity as they happen. | 2026-08-05T19:39:31.311323+00:00 | — |
| `59030434-7692-42e7-8d6b-0508c991d0e6` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | thread_id scopes the conversation (message history, checkpoints), while context carries per-run data your tools and middleware read at invocation time. Both are commonly passed together. See tool context and Runtime for more. | 2026-08-05T19:39:31.311323+00:00 | — |
| `61a3b480-8e12-4cd1-8729-c07030fb871c` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | If you also need to pass per-run configuration (such as a user ID, API keys, or feature flags) to tools and middleware, pass it as context alongside config. Define the shape of that data with context_schema and access it through runtime.context: | 2026-08-05T19:39:31.311323+00:00 | — |
| `c44c2d54-edfa-4854-9aad-edc1a7ec4b42` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | Every model call has a fixed context window. As an agent runs, that window fills with accumulating history, tool results, and intermediate steps. Summarization compresses history before overflow hits; memory loads persistent instructions at startup so knowledge carries across sessions; skills surface domain knowledge on demand rather than loading everything upfront. | 2026-08-05T19:39:31.311323+00:00 | — |
| `b543b3cf-8b08-469a-ad21-de147ff58a04` | langchain | LangChain agents | LangChain | https://docs.langchain.com/oss/python/langchain/agents | documentation | Complex tasks often exceed what one context window can handle. Delegation lets the main agent break work into pieces, hand them to subagents that each run in their own isolated context, and stay focused on coordination rather than execution. Work can run in parallel; the main agent’s context stays clean. | 2026-08-05T19:39:31.311323+00:00 | — |
| `6370c478-0626-4d98-8eb6-3423e870551a` | openai | OpenAI API models | OpenAI | https://developers.openai.com/api/docs/models | documentation | ### Capabilities<br><br>  Browser<br><br>  Computer use<br><br>  Voice<br><br>  Plugins<br><br>  Web search<br><br>  Image generation<br><br>  Image inputs<br><br>  Appshots<br><br>  Chrome extension<br><br>  Work with files | 2026-08-05T19:40:05.877916+00:00 | — |
| `06ab29f4-7ec9-47d1-8bb6-eb8fdae147b8` | openai | OpenAI API models | OpenAI | https://developers.openai.com/api/docs/models | documentation | ## Choosing a model<br><br>If you're not sure where to start, use GPT-5.6 Sol, our flagship model for complex reasoning and coding. Choose GPT-5.6 Terra to balance intelligence and cost, or GPT-5.6 Luna for cost-sensitive, high-volume workloads.<br><br>All latest OpenAI models support text and image input, text output, multilingual capabilities, and vision. Models are available via the Responses API and our Client SDKs. | 2026-08-05T19:40:05.877916+00:00 | — |
| `3f230b8b-7b6a-47b7-b44d-53ee44bd2190` | openai | OpenAI structured outputs guide | OpenAI | https://developers.openai.com/api/docs/guides/structured-outputs | documentation | ### Build tool workflows<br><br>  Skills<br><br>  Tool search<br><br>  Programmatic tool calling | 2026-08-05T19:43:41.427349+00:00 | — |
| `8238b406-2c2f-4fa1-8ad0-f519ebdaea10` | openai | OpenAI API models | OpenAI | https://developers.openai.com/api/docs/models | documentation | ### Build tool workflows<br><br>  Skills<br><br>  Tool search<br><br>  Programmatic tool calling | 2026-08-05T19:40:05.877916+00:00 | — |
| `0bc12e1d-d808-4134-863a-211b9113dfda` | openai | OpenAI model and Responses guidance | OpenAI | https://developers.openai.com/api/docs/guides/latest-model | documentation | To use Programmatic Tool Calling, add the programmatic_tool_calling tool and opt eligible tools in with allowed_callers. Update your application to handle program items, program-issued function calls, and program_output items while preserving each call’s call_id and caller linkage. See the Programmatic Tool Calling guide for request and continuation examples. | 2026-08-05T19:43:08.245630+00:00 | — |
| `64a0da5e-8bc5-4a37-9cab-0de3b944006e` | openai | OpenAI model and Responses guidance | OpenAI | https://developers.openai.com/api/docs/guides/latest-model | documentation | #### Choose Programmatic Tool Calling by task shape<br><br>Programmatic Tool Calling (PTC) works best for bounded workflows where code can process several tool results or large intermediate outputs and return a much smaller structured result. Use it for filtering, joining, ranking, deduplication, aggregation, validation, or other predictable processing.<br><br>Multiple, parallel, or dependent calls alone do not justify Programmatic Tool Calling. Prefer direct, non-PTC tool calls when:<br><br>One call is sufficient<br><br>The intermediate outputs are already small<br><br>Each result may change the model’s next decision<br><br>An action requires approval<br><br>The final output must preserve citations or native artifacts | 2026-08-05T19:43:08.245630+00:00 | — |
| `f21a2fde-68c1-4202-9d3d-ad50a2b30816` | openai | OpenAI model and Responses guidance | OpenAI | https://developers.openai.com/api/docs/guides/latest-model | documentation | Programmatic Tool Calling: GPT-5.6 can write JavaScript to call eligible tools, pass results between calls, and process intermediate outputs in a hosted runtime. Use Programmatic Tool Calling for bounded, tool-heavy workflows that do not require fresh model judgment between each step. Programmatic Tool Calling is ZDR-compatible with no additional container costs. | 2026-08-05T19:43:08.245630+00:00 | — |
| `26e8adbc-8437-4cbe-bbe4-1cb35715d33f` | openai | OpenAI model and Responses guidance | OpenAI | https://developers.openai.com/api/docs/guides/latest-model | documentation | Use direct tool calls for [semantic judgment, approval, or final validation].<br></tool_orchestration> | 2026-08-05T19:43:08.245630+00:00 | — |
| `43b1e9da-8f11-448b-9458-bc15a2618d1a` | anthropic | Claude models | Anthropic | https://platform.claude.com/docs/en/about-claude/models | documentation | Claude Fable 5 (claude-fable-5) is Anthropic's most capable widely released model. Claude Mythos 5 (claude-mythos-5) shares Claude Fable 5's specs and pricing and joins the invitation-only Claude Mythos Preview (claude-mythos-preview) within Project Glasswing. See Introducing Claude Fable 5 and Claude Mythos 5 for launch details and API changes. | 2026-08-06T03:11:53.992428+00:00 | — |
| `52a3db01-3f5a-40f3-9f2c-659b405aa587` | anthropic | Claude models | Anthropic | https://platform.claude.com/docs/en/about-claude/models | documentation | You can query model capabilities and token limits programmatically with the Models API. The response includes max_input_tokens, max_tokens, and a capabilities object for every available model. | 2026-08-06T03:11:53.992428+00:00 | — |
| `7fe98dfc-4138-4f36-9006-03bd7795e68b` | anthropic | Anthropic tool use | Anthropic | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | documentation | Tool use lets Claude call functions that you define or that Anthropic provides. Claude determines when to call a tool based on the user's request and the tool's description. It then returns a structured call that your application executes (client tools) or that Anthropic executes (server tools). | 2026-08-06T03:12:02.319927+00:00 | — |
| `cef2504b-6c4c-42ae-bb31-10e01377e1c7` | anthropic | Anthropic tool use | Anthropic | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | documentation | Tools differ primarily by where the code executes. Client tools (including user-defined tools and tools with Anthropic-defined schemas, such as bash and text_editor) run in your application. Claude responds with stop_reason: "tool_use" and one or more tool_use blocks. Your code executes the operation and sends back a tool_result. Server tools (such as web_search, web_fetch, code_execution, and tool_search) run on Anthropic's infrastructure: you see the results directly without handling execution, unless Claude calls the tool in the same group of parallel tool calls as one of your client tools (see Stop reasons and fallback). | 2026-08-06T03:12:02.319927+00:00 | — |
| `cc37831c-ec78-4614-8ee6-44fa0130b084` | anthropic | Anthropic tool use | Anthropic | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | documentation | To require a tool call rather than rely on prompting, set tool_choice. | 2026-08-06T03:12:02.319927+00:00 | — |
| `c6e4a38a-3fff-4350-a577-4877d4afcdb3` | anthropic | Anthropic tool use | Anthropic | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | documentation | With the default tool_choice of {"type": "auto"}, Claude determines on each turn whether to call a tool or respond directly. It calls a tool when the request maps to that tool's described capability and the answer isn't already in context. It responds directly for stable knowledge, creative tasks, and conversational turns. | 2026-08-06T03:12:02.319927+00:00 | — |
| `565d6e79-4067-4282-859e-855bd862a287` | anthropic | Anthropic tool use | Anthropic | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | documentation | Handle tool calls covers each step in detail, including result formatting and error signaling; Parallel tool use covers responses that call several tools at once. To skip writing this round trip yourself, use Tool Runner: the SDKs execute your tools and send the results back automatically. | 2026-08-06T03:12:02.319927+00:00 | — |
| `40ef5025-d26b-413e-a62f-c6d54127efbb` | anthropic | Anthropic documentation overview | Anthropic | https://platform.claude.com/docs/en/overview | documentation | Context management | 2026-08-06T03:11:24.815053+00:00 | — |
| `00f2f82e-aa93-4d9c-9a73-05da1ebd72cf` | anthropic | Anthropic tool use | Anthropic | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | documentation | Context windowsCompactionContext editingPrompt cachingMid-conversation system messages and tool changesBuild an orchestration modeCache diagnostics (beta)Token counting | 2026-08-06T03:12:02.319927+00:00 | — |
| `73443aa3-3fbe-4331-b3dd-15f1bf111dbd` | anthropic | Anthropic documentation overview | Anthropic | https://platform.claude.com/docs/en/overview | documentation | Context windowsCompactionContext editingPrompt cachingMid-conversation system messages and tool changesBuild an orchestration modeCache diagnostics (beta)Token counting | 2026-08-06T03:11:24.815053+00:00 | — |

## Estado de revisión

Revisión del owner confirmada el 2026-08-07 para el run
`ed9e093f-74ed-4d47-a5c6-8a05ace0e505`: las 11 celdas con citas están directamente respaldadas
por su evidencia (11/11; precisión de citas `1.0`) y `openai/context` queda correctamente como
`expected unsupported`.

T040 se cierra porque las métricas de latencia exigidas también están registradas en el run vivo
optimizado `2a317ed1-a0b9-4f6c-9227-f6fcdf93f382`: progreso útil `0 ms` y latencia terminal
`18,590 ms`. El run anterior `aae76ef0-931b-49bc-9b42-6686f773fcbb` se conserva sin sobrescribir
como evidencia de la regresión real que motivó T043.
