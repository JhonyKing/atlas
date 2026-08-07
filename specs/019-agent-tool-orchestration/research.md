# Research: Agent Tool Orchestration

## Decision 1: Use a typed allowlisted registry

- **Decision**: Every capability is a versioned `ToolDefinition` with input/output schemas, scopes,
  side-effect metadata, approval policy, timeout, budget, and availability. The planner can select
  only registry IDs.
- **Rationale**: A free-form LLM tool name is an authorization vulnerability. A registry makes the
  user-visible product, API contract, tests, and LangSmith traces agree on one vocabulary.
- **Alternatives considered**:
  - Let the model call arbitrary Python functions: rejected because it breaks least privilege and
    makes prompt injection an authorization path.
  - Keep independent screens only: rejected because it does not provide a coherent agent workspace.

## Decision 2: Keep domain services behind tool adapters

- **Decision**: Tool adapters call existing answer, comparison, report, news, corpus, auth, private,
  and review services. They return neutral typed results with evidence/artifact references.
- **Rationale**: The agent should orchestrate existing capabilities instead of duplicating business
  logic or provider response objects.
- **Alternatives considered**:
  - Rewrite each feature inside a giant agent graph: rejected because it would increase coupling and
    make regression evidence harder to isolate.

## Decision 3: Separate planning from authorization and execution

- **Decision**: The planner proposes a validated plan; policy/approval gates authorize it; the
  executor runs the bounded plan and emits events.
- **Rationale**: Model output is untrusted. A clear boundary makes safety, replay, cancellation,
  auditing, and deterministic tests possible.
- **Alternatives considered**:
  - Execute directly from model tool-call JSON: rejected because validation and approval would be
    implicit and bypassable.

## Decision 4: Use event-sourced run visibility without exposing raw content

- **Decision**: Emit ordered typed events for planning, approval, tool call/result, verification,
  completion, abstention, cancellation, and failure. Store safe summaries and IDs, not secrets or
  private excerpts unless the existing evidence contract explicitly permits them.
- **Rationale**: Operators and reviewers need to understand agent behavior, while LangSmith and UI
  traces must respect privacy boundaries.
- **Alternatives considered**:
  - Log only the final answer: rejected because it cannot explain tool selection, safety decisions,
    or latency/cost.

## Decision 5: Start with bounded plans

- **Decision**: Initial execution supports finite sequential plans with explicit dependencies,
  budgets, timeouts, checkpoint/replay, and cancellation. Arbitrary loops/code are out of scope.
- **Rationale**: This is sufficient to demonstrate agentic orchestration while keeping behavior
  deterministic enough for portfolio-grade evaluation.
- **Alternatives considered**:
  - Open-ended autonomous loops: rejected until measured demand and stronger evaluation evidence.
