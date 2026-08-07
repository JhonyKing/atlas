# Feature Specification: Agent Tool Orchestration

**Feature Branch**: `019-agent-tool-orchestration`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User request to turn ATLAS into an agent whose capabilities are exposed as selectable tools instead of isolated LLM calls.

## User Scenarios & Testing

### User Story 1 - Choose an ATLAS capability (Priority: P1)

As a user, I want ATLAS to show me the available capabilities and let me choose what I want to do, so I can ask for an answer, comparison, report, news briefing, corpus inspection, or private-data action without guessing which screen or endpoint to use.

**Why this priority**: The current application exposes several independent forms. A coherent tool-driven agent is the product behavior the user wants to demonstrate.

**Independent Test**: Open the app, select each read-only capability from the tool catalog, submit its required inputs, and verify that the selected tool and resulting evidence are shown.

**Acceptance Scenarios**:

1. **Given** a new session, **When** the user opens the agent workspace, **Then** ATLAS displays a localized catalog of available tools with purpose, required inputs, side-effect level, and whether human approval is required.
2. **Given** the user selects `cited_answer`, **When** the user submits a technical question, **Then** the agent invokes the answer workflow through a typed tool contract and renders its existing evidence/abstention result.
3. **Given** the user selects `comparison`, `report`, `daily_news`, or `corpus_status`, **When** the user completes the tool-specific form, **Then** the same agent run records the selected tool, arguments, tool result, evidence IDs, and final user-facing output.
4. **Given** Spanish is selected, **When** the user opens the catalog and runs a tool, **Then** labels, validation, progress, errors, and result status are Spanish while tool IDs and schemas remain English-canonical.

### User Story 2 - Let the agent plan and call tools safely (Priority: P1)

As a user, I want the agent to understand a natural-language request and propose or execute the appropriate tool, so ATLAS can orchestrate a multi-step research task without turning external text into instructions.

**Why this priority**: A static menu alone is not an agent. The agent must select from an allowlisted registry, validate arguments, and preserve evidence through each step.

**Independent Test**: Submit natural-language requests for an answer, comparison, report, news briefing, and an unsafe/private action; inspect the plan, tool calls, validated outputs, and abstention/approval behavior.

**Acceptance Scenarios**:

1. **Given** a supported research request, **When** the agent plans, **Then** it emits a typed plan containing one or more allowlisted tool IDs, validated arguments, dependencies, and an expected output contract before execution.
2. **Given** a tool result, **When** the agent composes a response, **Then** every factual claim remains linked to evidence returned by a tool and insufficient evidence produces the existing abstention contract.
3. **Given** a request that requires multiple tools, **When** the workflow executes, **Then** dependencies, budgets, timeouts, cancellation, checkpoint/replay, and partial failure states are visible in the run timeline.
4. **Given** an unknown tool ID, malformed arguments, prompt injection, or a tool outside the user's authorization, **When** the agent receives it, **Then** it rejects the call without invoking a provider or connector.

### User Story 3 - Approve side effects and private-data actions (Priority: P1)

As a user, I want explicit confirmation before an action can change data or use private resources, so the agent cannot upload, delete, ingest, publish, or access another user's information by accident.

**Why this priority**: The tool model expands the action surface. Human control and ownership checks must be part of the agent contract, not a UI promise.

**Independent Test**: Run private upload, private deletion, ingestion, report publication, and connector actions with and without approval and with two user identities; verify the tool gate, audit event, ownership result, and repeat-safe deletion.

**Acceptance Scenarios**:

1. **Given** a side-effecting tool, **When** the agent proposes it, **Then** the UI shows the exact tool, bounded arguments, data target, retention impact, and approval action before execution.
2. **Given** an approval, **When** the authorized user confirms within the expiry window, **Then** exactly one idempotent execution occurs and the audit record links approval, tool call, result, and actor.
3. **Given** rejection, expiry, cancellation, duplicate replay, or a different user, **When** execution is attempted, **Then** no side effect occurs and the run records a safe reason.

### User Story 4 - Inspect and evaluate agent runs (Priority: P2)

As an operator and portfolio reviewer, I want a transparent run timeline and LangSmith-compatible trace, so I can explain what the agent decided, which tools ran, what evidence they returned, and where latency/cost/errors occurred.

**Why this priority**: Agentic engineering must be observable and evaluable; an opaque LLM call is not sufficient portfolio evidence.

**Independent Test**: Execute successful, abstained, rejected, timed-out, and failed-provider runs, then inspect the timeline, trace metadata, redactions, tool/evidence mapping, and evaluation record.

**Acceptance Scenarios**:

1. **Given** an agent run, **When** the user opens its timeline, **Then** it shows request, plan, approval, tool calls, tool results, evidence IDs, verification, final status, latency, and cost without secrets or private content.
2. **Given** LangSmith is configured, **When** a run executes, **Then** trace spans are tagged with environment, run ID, tool ID/version, model, locale, corpus snapshot, and outcome while content redaction remains enforced.
3. **Given** a regression in tool selection, evidence mapping, safety, latency, or cost, **When** the evaluation suite runs, **Then** the relevant gate fails with a reproducible fixture or recorded live-eval reference.

## Edge Cases

- The model asks for two tools that conflict or have a dependency cycle; the agent must reject the plan and explain the conflict.
- A tool returns partial or contradictory evidence; the final answer must preserve the typed relation and must not invent a value.
- A tool times out or a provider is unavailable; the run must be cancellable and must not claim completion.
- The browser disconnects during a run; a checkpoint can be resumed safely without duplicating side effects.
- A user changes locale during a run; schema IDs and evidence IDs remain stable while rendered messages use the selected locale.
- A prompt injection appears in a source excerpt or tool output; it remains data and cannot alter system instructions or authorize another tool.
- A tool is disabled by beta policy, missing credentials, over quota, or stale corpus; the catalog and run report its unavailable state rather than silently using a fixture.
- The same approval key is replayed; the side-effecting tool remains idempotent and produces at most one mutation.
- A report or document is generated; its artifact ID, evidence IDs, source versions, and retention status remain visible in the run.

## Requirements

### Functional Requirements

- **FR-001**: ATLAS MUST expose a versioned tool catalog containing at least `cited_answer`, `comparison`, `report`, `daily_news`, `corpus_status`, `private_resources`, `private_upload`, `private_delete`, and `human_review` capabilities.
- **FR-002**: Each catalog entry MUST declare an English-canonical tool ID, localized name/description, input schema, output schema, required scopes, side-effect level, approval requirement, timeout, budget, and availability status.
- **FR-003**: The agent MUST accept an explicit tool selection or infer a proposed tool plan from a natural-language request, but execution MUST be limited to the allowlisted catalog.
- **FR-004**: The agent MUST validate model-produced tool names and arguments against typed schemas before any tool or provider call; invalid calls MUST fail closed.
- **FR-005**: Read-only tools MUST reuse the existing answer, comparator, report, news, corpus, and evidence contracts rather than duplicating domain logic.
- **FR-006**: Side-effecting and private-data tools MUST enforce identity, scope, ownership, quota, consent, retention, and explicit human approval before execution.
- **FR-007**: Approval MUST bind the actor, tool version, normalized arguments, target resource, expiry, and idempotency key; replay or mutation with different arguments MUST be rejected.
- **FR-008**: The agent MUST support bounded sequential tool plans, dependency validation, cancellation, timeout, budget, checkpoint/replay, and safe partial-failure states.
- **FR-009**: Tool results MUST preserve evidence IDs, provenance, source versions, bounded excerpts, artifact IDs, and typed evidence relations so final claims remain verifiable.
- **FR-010**: The agent MUST emit a versioned run event stream for request, planning, approval, tool call, tool result, verification, completion, abstention, cancellation, and failure events.
- **FR-011**: The web application MUST provide a localized agent workspace with tool selection, required-input forms, approval cards, run timeline, result/artifact links, and clear unavailable/error states.
- **FR-012**: The API MUST expose typed agent endpoints for catalog, plan, execute, events/status, approval, cancellation, and resume without exposing provider-specific response objects.
- **FR-013**: Agent model calls MUST use the existing provider adapter and default GPT-5.6 Luna configuration; model output MUST be treated as an untrusted proposal, never as authorization.
- **FR-014**: LangSmith/OpenTelemetry traces MUST correlate one agent run across planner, tools, retrieval, model, verification, persistence, and rendering with redacted metadata for tool ID/version, model, tokens, cost, latency, locale, corpus, and outcome.
- **FR-015**: The agent MUST produce evaluation records for tool-selection accuracy, argument validity, evidence coverage, abstention, safety/approval, latency, cost, and artifact correctness; deterministic fixtures and live runs MUST be distinguished.
- **FR-016**: Feature documentation MUST describe the tool registry, trust boundaries, approval model, event lifecycle, run/evaluation evidence, and how existing feature screens map to tools.

### Key Entities

- **ToolDefinition**: Versioned catalog entry with input/output contracts, policy metadata, scope, availability, and localized copy.
- **AgentPlan**: Validated sequence/graph of tool calls with dependencies, normalized arguments, budget, and expected output.
- **ToolCall**: One proposed or executed invocation with actor, arguments hash, status, idempotency key, timing, and evidence/artifact references.
- **Approval**: Human authorization bound to a tool version, arguments, target, actor, expiry, and decision.
- **AgentRunEvent**: Append-only lifecycle event with run ID, sequence, event type, safe payload, correlation ID, and trace linkage.
- **AgentRun**: User request, locale, plan, tool calls, checkpoint, final status, evidence/artefact summary, cost, and error state.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A new user can select a catalog tool and start a valid answer, comparison, report, news, or corpus task in under 60 seconds in either supported locale.
- **SC-002**: 100% of executed tool calls in the contract suite use an allowlisted ID and pass schema, scope, budget, and timeout validation before execution.
- **SC-003**: 100% of tested side-effecting/private-data scenarios require a matching unexpired approval and ownership check; rejected, expired, or replayed approvals cause zero mutations.
- **SC-004**: At least 95% of claims in the representative agent evaluation set have a valid evidence mapping, and unsupported/contradictory cases abstain or preserve the relation instead of inventing a value.
- **SC-005**: A run timeline renders the complete lifecycle and event order for successful, abstained, cancelled, failed, and resumed runs with no secret/private-content leakage.
- **SC-006**: Each representative run has one correlated redacted trace containing tool, model, locale, corpus, latency, token/cost, and outcome metadata.
- **SC-007**: A disconnected client can resume a read-only run without duplicating a tool call, and a replayed side-effect approval causes at most one mutation.
- **SC-008**: A deliberately invalid tool name, malformed argument, prompt-injected authorization, dependency cycle, budget overflow, or provider failure blocks execution and produces a diagnosable run event.
- **SC-009**: The tool registry and agent run documentation allow a reviewer to map every existing user-facing feature to a tool, its contract, its safety level, and its evaluation evidence.

## Scope Boundaries

- This feature introduces the agent control/orchestration layer and its user-facing workspace. It reuses existing feature domain services; it does not rewrite retrieval, comparison, reports, news, auth, or private-data internals.
- The first slice supports bounded, typed tool plans. It does not permit arbitrary code execution, arbitrary URLs, self-modifying tools, or unconstrained autonomous loops.
- Provider credentials, LangSmith credentials, and external deployment remain environment concerns from Feature 018; local fake/no-op providers may be used only where the run explicitly records fixture mode.
- Existing standalone screens may remain as compatibility entry points during migration, but the agent workspace is the canonical path for the portfolio demonstration.

## Assumptions

- Existing Feature 006 agent state/checkpoint/review contracts are reusable but require a registry and tool-call event model.
- Existing endpoints and services already expose enough typed contracts for answer, comparison, reports, news, corpus, auth, and private-data actions.
- GPT-5.6 Luna is the default planner model through the existing provider adapter; routing/evaluation can select another configured provider without changing tool contracts.
- Anonymous users can use read-only tools within existing quota policy; authentication and ownership remain mandatory for private or side-effecting tools.
- Human approval is required for mutation, publication, ingestion, deletion, and private-data access that is not already covered by an explicit user request and policy.
