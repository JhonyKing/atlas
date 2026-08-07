# Feature Specification: Model Router, GPT-5.6 Luna, and Cost Controls

**Feature Branch**: `codex/008-model-router-gpt56-luna`  
**Created**: 2026-08-06  
**Status**: Draft  
**Input**: PRD MOD-001 through MOD-010

## User Scenarios & Testing

### User Story 1 — Choose an appropriate model (P1)

As an ATLAS request, I want a provider-independent router to select `gpt-5.6-luna` by default
and adjust reasoning by task complexity, freshness, contradiction, and report depth.

**Acceptance**: selection is deterministic, records model/version/reasoning effort, and never
allows user input to choose an unapproved provider or model.

### User Story 2 — Fail safely across providers (P1)

As an operator, I want timeouts, bounded retries, circuit breaking, and provider fallback so a
temporary provider failure becomes a controlled response without duplicate side effects.

**Acceptance**: retries use jitter and a cap; an open circuit skips the provider; fallback is
recorded; secrets and prompt content are not emitted to logs or telemetry.

### User Story 3 — Control cost and prove changes (P1)

As a portfolio engineer, I want effective-dated prices, token/cost telemetry, budgets, caching,
batch evaluation and an A/B gate so model changes are approved by evidence rather than claims.

**Acceptance**: cost estimates use the active price version, budget breaches stop optional work,
cache keys include corpus/model/prompt versions, and A/B results are reproducible.

## Functional Requirements

- **FR-MOD-001**: The router MUST expose provider-independent typed model selection and fallback contracts.
- **FR-MOD-002**: The default answer model MUST be `gpt-5.6-luna`, configurable only by server settings.
- **FR-MOD-003**: Selection MUST use task complexity, freshness, contradiction, and report depth signals.
- **FR-MOD-004**: Provider adapters MUST remain outside graph nodes and preserve a common response contract.
- **FR-MOD-005**: Retry, timeout, circuit-breaker, and fallback behavior MUST be bounded and observable.
- **FR-MOD-006**: Embedding selection MUST support locale/provider profiles without changing Evidence.
- **FR-MOD-007**: Pricing MUST be effective-dated and token/cost telemetry MUST identify its price version.
- **FR-MOD-008**: Cache and evidence-pack keys MUST include model, prompt, retrieval and corpus versions.
- **FR-MOD-009**: Batch evaluation MUST support reproducible model comparison and A/B promotion gates.
- **FR-MOD-010**: Secrets, prompts, excerpts, and private data MUST NOT appear in router logs by default.

## Success Criteria

- **SC-MOD-001**: 100% of router contract tests select Luna by default and reject unknown models.
- **SC-MOD-002**: 100% of simulated timeout/429/5xx cases terminate within bounded retry policy.
- **SC-MOD-003**: 100% of cost records include model, price version, tokens, and estimated cost.
- **SC-MOD-004**: Cache invalidation tests remove stale entries when any version component changes.
- **SC-MOD-005**: A/B gate refuses promotion when quality, latency, or cost regresses.

## Edge Cases

- Missing provider key: use the local no-op/demo adapter only in development; production fails closed.
- Unknown model or price version: reject before any provider call.
- Budget exhausted: return a controlled quota/budget status and do not retry indefinitely.
- Provider returns malformed output: discard it and use the typed fallback path.
- Cache contains a private evidence pack: enforce tenant ownership before returning it.
