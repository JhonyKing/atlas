# T040 live citation review — 2026-08-07

Run: `7b10f03e-fd20-47c6-9ec8-004ae7bbd09f`  
Snapshot: `660b0578-992f-43d2-9722-fa0c49568bbd`  
Runtime: 68,751 ms, HTTP 200, terminal event `comparison.completed`.

## How to review

For each row, open the evidence IDs in the local corpus and answer: “Does at least one cited
excerpt directly support the comparison cell?” Record `yes` or `no` in the final column. Do not
infer support from the title alone. Empty evidence means `no evidence`, not an automatic citation
failure.

| Technology | Criterion | State | Evidence IDs | Ground truth supported |
|---|---|---|---|---|
| langgraph | capability | partial | `b744c1a8-f160-4aa4-94b9-059d2a9fe19c` | pending |
| langgraph | tool_calling | partial | `a2327062`, `de93d415`, `e9c05c2d` | pending |
| langgraph | context | partial | `0813c640`, `8e145d01`, `6db34524`, `f78a02b9` | pending |
| langchain | capability | partial | `e29508eb`, `f450f5a6` | pending |
| langchain | tool_calling | partial | `3744fd33`, `48fa7485`, `eb377e82`, `32fd5e1e` | pending |
| langchain | context | partial | `59030434`, `61a3b480`, `c44c2d54`, `b543b3cf` | pending |
| openai | capability | partial | `6370c478` | pending |
| openai | tool_calling | partial | `09a0753f`, `0bc12e1d`, `f21a2fde` | pending |
| openai | context | unsupported | none | pending — expected no support |
| anthropic | capability | partial | `43b1e9da` | pending |
| anthropic | tool_calling | partial | `7fe98dfc`, `cef2504b`, `565d6e79`, `cc37831c` | pending |
| anthropic | context | unsupported | none | pending — expected no support |

## Evidence catalog

| Short ID | Source title | URL | Excerpt |
|---|---|---|---|
| `b744c1a8` | LangGraph overview | https://docs.langchain.com/oss/python/langgraph/overview | Capabilities include persistence, checkpointers, stores, fault tolerance, event streaming, interrupts, time travel, memory and subgraphs. |
| `a2327062` | LangGraph interrupts | https://docs.langchain.com/oss/python/langgraph/interrupts | A tool node performs tool calls and returns tool messages. |
| `de93d415` | LangGraph interrupts | https://docs.langchain.com/oss/python/langgraph/interrupts | Tool calls can be paused before execution for review and editing. |
| `e9c05c2d` | LangGraph interrupts | https://docs.langchain.com/oss/python/langgraph/interrupts | Interrupts can pause execution whenever a tool is invoked for approval, editing or cancellation. |
| `0813c640` | LangGraph graph API | https://docs.langchain.com/oss/python/langgraph/graph-api | `context_schema` passes runtime context to nodes. |
| `8e145d01` | LangGraph graph API | https://docs.langchain.com/oss/python/langgraph/graph-api | Example runtime context contains a `user_id`. |
| `6db34524` | LangGraph graph API | https://docs.langchain.com/oss/python/langgraph/graph-api | Runtime contains context and execution controls. |
| `f78a02b9` | LangGraph graph API | https://docs.langchain.com/oss/python/langgraph/graph-api | Context is passed into the graph through `invoke`. |
| `e29508eb` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | Agents can configure model, tools and system prompt. |
| `f450f5a6` | LangChain overview | https://docs.langchain.com/oss/python/langchain/overview | `create_agent` is a configurable harness extensible through middleware. |
| `3744fd33` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | An agent is a model calling tools in a loop until a task completes. |
| `48fa7485` | LangChain middleware | https://docs.langchain.com/oss/python/langchain/middleware/overview | The core loop calls a model, lets it choose tools, then finishes. |
| `eb377e82` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | Agents can act through tools, filesystem and code execution. |
| `32fd5e1e` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | Streaming surfaces progress during multiple tool calls. |
| `59030434` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | `thread_id` scopes history while context carries per-run data. |
| `61a3b480` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | Per-run configuration can be passed as context. |
| `c44c2d54` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | Summarization and memory manage context-window growth. |
| `b543b3cf` | LangChain agents | https://docs.langchain.com/oss/python/langchain/agents | Delegation breaks complex tasks into isolated subagents. |
| `6370c478` | OpenAI API models | https://developers.openai.com/api/docs/models | Model capabilities include browser, computer use, voice, web search and image generation. |
| `09a0753f` | OpenAI model and Responses guidance | https://developers.openai.com/api/docs/guides/latest-model | Programmatic tool calling is available. |
| `0bc12e1d` | OpenAI model and Responses guidance | https://developers.openai.com/api/docs/guides/latest-model | Programmatic tool calling requires preserving call linkage and handling program outputs. |
| `f21a2fde` | OpenAI model and Responses guidance | https://developers.openai.com/api/docs/guides/latest-model | GPT-5.6 can write JavaScript to call eligible tools in a hosted runtime. |
| `43b1e9da` | Claude models | https://platform.claude.com/docs/en/about-claude/models | Claude Fable 5 is listed as a widely released model. |
| `7fe98dfc` | Anthropic tool use | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | Claude can call user-defined or Anthropic-provided tools. |
| `cef2504b` | Anthropic tool use | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | Client and server tools return structured tool-use blocks and results. |
| `565d6e79` | Anthropic tool use | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | Tool Runner handles result formatting and error signaling. |
| `cc37831c` | Anthropic tool use | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | `tool_choice` can require a tool call. |
