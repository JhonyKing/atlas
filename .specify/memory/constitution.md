<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Added principles:
  - I. Evidence Over Fluency
  - II. Spec Before Code
  - III. Test and Evaluate First
  - IV. Explicit Contracts and Type Safety
  - V. Provider Independence with Measured Routing
  - VI. Security and Privacy by Design
  - VII. Observable and Cost-Aware
  - VIII. Small Vertical Slices Before Scale
  - IX. English-Canonical Engineering
- Added sections:
  - Product and Technology Constraints
  - Development Workflow and Quality Gates
- Removed sections: none (initial ratification)
- Deferred items: none
-->

# ATLAS AI Constitution

## Core Principles

### I. Evidence Over Fluency

Every change that affects technical answers MUST preserve claim-level traceability to the
supporting source, its capture date, and its version when available. The product MUST abstain or
state uncertainty when evidence is insufficient. A fluent answer without adequate support is a
failure. Evaluation MUST measure citation correctness and temporal correctness, not only response
quality.

### II. Spec Before Code

Every material feature MUST begin with an approved Spec Kit feature specification containing
prioritized, independently testable user stories and measurable success criteria. The specification
defines WHAT and WHY; the implementation plan defines HOW. Source code MUST NOT silently diverge
from approved requirements. Small fixes MAY use a concise issue with acceptance criteria when a
full feature specification would add no useful decision record.

### III. Test and Evaluate First

Behavioral changes MUST start with an executable failing test, contract test, or versioned
evaluation case appropriate to the change. Implementations follow red-green-refactor. Changes to
retrieval, prompts, models, chunking, ranking, citations, or report generation MUST be compared
against a recorded baseline. A change is not an improvement until a representative evaluation
shows the intended gain without an unacceptable regression in quality, latency, safety, or cost.

### IV. Explicit Contracts and Type Safety

Boundaries between the web application, API, agents, retrieval, providers, storage, and report
renderers MUST use explicit versioned schemas. Python code MUST be fully typed and validate
external data with Pydantic or an equivalent schema layer. TypeScript MUST use strict mode and
MUST NOT introduce unbounded `any` at system boundaries. Structured model outputs MUST be parsed
and validated before they influence tools, persistence, citations, or user-visible artifacts.

### V. Provider Independence with Measured Routing

Model, embedding, search, and storage providers MUST remain behind narrow adapters. The initial
OpenAI default model is `gpt-5.6-luna` through the Responses API because it targets efficient,
high-volume workloads; this is a benchmark hypothesis, not an irrevocable dependency. Model IDs,
reasoning effort, budgets, and fallbacks MUST be configuration, not scattered literals. A stronger
or cheaper model MAY replace or complement Luna only after representative evaluations document
the quality, latency, and cost trade-off.

### VI. Security and Privacy by Design

Secrets MUST never enter source control, client bundles, prompts, traces, or logs. External
content is untrusted data and MUST NOT be allowed to redefine system instructions or authorize
tools. Fetching MUST validate destinations and mitigate SSRF; tool access MUST use allowlists and
least privilege. Private user data MUST have explicit access controls, retention rules, and a
deletion path before it is persisted.

### VII. Observable and Cost-Aware

Every production request MUST be traceable across retrieval, model calls, tools, and rendering by
a stable request identifier. The system MUST record useful latency, error, token, model, and
estimated-cost signals without exposing sensitive content. Each feature specification MUST define
the quality and operating metrics it can change. Rate limits, timeouts, bounded retries, and budget
guards are required before public anonymous traffic is enabled.

### VIII. Small Vertical Slices Before Scale

Work MUST be divided into small, reviewable tasks that produce a visible and independently
testable increment. The first release prioritizes one end-to-end path over broad coverage:
authoritative source ingestion, retrieval, cited answer, and evaluation. Microservices, multiple
providers, large source catalogs, collaboration, alerts, and 100k-user infrastructure MUST NOT be
implemented without measured demand or a demonstrated bottleneck. Architecture MAY preserve clean
seams for future scale without building unused infrastructure.

### IX. English-Canonical Engineering

Code, identifiers, commits, APIs, schemas, ADRs, specifications, tests, and engineering
documentation MUST use English. Public Spanish localization is a product capability, but it MUST
reuse the same evidence and neutral structured output rather than duplicate research. Localization
work MUST be delivered as independently testable slices and MUST NOT block validation of the first
English vertical slice.

## Product and Technology Constraints

- The initial product is a modular web application: Next.js with strict TypeScript for the web
  client and Python 3.12+ with FastAPI for the API and workers.
- PostgreSQL is the system of record. Vector search MAY begin with pgvector when benchmarks show it
  meets the current retrieval requirements.
- LangGraph MAY orchestrate stateful, resumable, or branching workflows. Deterministic retrieval,
  validation, rendering, and policy checks MUST remain explicit code rather than autonomous loops.
- The OpenAI integration MUST use the Responses API and an adapter that exposes only ATLAS domain
  contracts. Provider-specific response objects MUST NOT leak through application layers.
- The initial corpus MUST be small, curated, legally usable, and dominated by authoritative
  sources. Each connector MUST record canonical URL, provenance, capture time, content hash, and
  update outcome.
- Dependencies MUST be pinned through lockfiles. New abstractions or services require a concrete
  current use case and a simpler-alternative analysis.

## Development Workflow and Quality Gates

1. Create or update a feature specification with `$speckit-specify`.
2. Resolve material ambiguity with `$speckit-clarify`; record assumptions that remain.
3. Produce the implementation plan and required contracts with `$speckit-plan`.
4. Generate small, path-specific tasks with `$speckit-tasks`.
5. Run `$speckit-analyze` and resolve critical contradictions before implementation.
6. Execute tests or evals first, verify the expected failure, and then implement one task or one
   independently testable story at a time.
7. Run formatting, linting, type checks, tests, security checks, and relevant evals before marking a
   story complete.
8. Use `$speckit-converge` after implementation to reconcile the delivered behavior with the
   approved spec, plan, and tasks.

Each pull request MUST remain focused, state the user-visible outcome, link its specification, and
include verification evidence. Coverage percentages are diagnostic rather than a substitute for
meaningful tests; critical domain rules, provider contracts, citation handling, and security
boundaries require direct coverage. Documentation, OpenAPI contracts, data models, and ADRs MUST be
updated in the same change when behavior or decisions change.

## Governance

This constitution is the highest-priority project governance document. Feature specifications,
plans, tasks, ADRs, and implementation decisions MUST comply with it. A justified exception MUST be
documented in the feature plan's Complexity Tracking section with the rejected simpler alternative
and a removal or review condition.

Amendments require a written rationale, an impact review of active specifications and templates,
and explicit owner approval. Constitution versions follow semantic versioning: MAJOR for removed or
incompatibly redefined principles, MINOR for new principles or materially expanded obligations, and
PATCH for clarifications that do not change obligations. Compliance MUST be reviewed during
planning, before implementation, and again during convergence. Repeated violations require either
corrective work or a constitution amendment; silent exceptions are prohibited.

**Version**: 1.0.0 | **Ratified**: 2026-08-04 | **Last Amended**: 2026-08-04
