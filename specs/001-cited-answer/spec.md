# Feature Specification: Verifiable Cited Answer

**Feature Branch**: `codex/001-cited-answer`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "Begin ATLAS AI from the approved PRD using Spec Kit, feature by feature. The first portfolio slice must demonstrate useful agentic research rather than a generic chat experience."

## Clarifications

### Session 2026-08-04

- Q: Which three official collections should form the initial corpus? -> A: LangGraph documentation, LangChain documentation, and OpenAI API documentation.
- Q: How frequently should the initial corpus refresh automatically? -> A: Daily automatic refresh with an operator-triggered refresh on demand.
- Q: How long may ATLAS retain anonymous questions and diagnostic traces? -> A: Retain pseudonymized content for 30 days, then delete the content and keep only aggregate metrics.
- Q: Should the initial corpus include official changelogs and release notes? -> A: Include documentation, changelogs, and official release notes for LangGraph, LangChain, and OpenAI.
- Q: How many free questions may an anonymous visitor ask in 24 hours? -> A: 10 questions per anonymous visitor in each rolling 24-hour period.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask a Technical Question (Priority: P1)

As an AI engineer, I can ask a natural-language question about the technologies covered by the
launch corpus and receive a concise answer whose principal factual claims link to supporting
evidence.

**Why this priority**: This is the smallest public experience that demonstrates ATLAS's core value:
turning fragmented technical information into a verifiable answer.

**Independent Test**: Select a question with known support in the launch corpus, submit it, and
confirm that the answer addresses the question and that each principal factual claim has at least
one navigable citation.

**Acceptance Scenarios**:

1. **Given** the launch corpus contains current evidence for a question, **When** a visitor asks the
   question, **Then** the visitor receives a concise answer with citations attached to its principal
   factual claims.
2. **Given** a question contains a product name, version, or date constraint, **When** the visitor
   submits it, **Then** the answer preserves those constraints or explicitly states that the corpus
   cannot satisfy them.
3. **Given** a valid question is being processed, **When** the answer takes more than one second to
   prepare, **Then** the visitor sees clear progress rather than an apparently frozen page.

---

### User Story 2 - Inspect the Evidence (Priority: P2)

As a skeptical reader, I can inspect the exact source behind a cited claim so that I can judge its
authority, freshness, and relevance without trusting ATLAS blindly.

**Why this priority**: Transparent evidence is the portfolio differentiator between ATLAS and a
generic conversational interface.

**Independent Test**: Open every citation in a prepared answer and confirm that each one exposes the
source title, publisher, canonical link, capture or publication date, and the supporting excerpt.

**Acceptance Scenarios**:

1. **Given** an answer contains a citation, **When** the reader opens it, **Then** the reader sees the
   supporting excerpt and source metadata before choosing whether to leave ATLAS.
2. **Given** the original source is still reachable, **When** the reader follows the source link,
   **Then** it opens the canonical source location in a new browser context.
3. **Given** a cited source has known version or release metadata, **When** evidence is displayed,
   **Then** that metadata is visible and is not presented as a certainty when it is unknown.

---

### User Story 3 - Receive an Honest Abstention (Priority: P3)

As an AI engineer, I receive an explicit abstention or uncertainty notice when the available
evidence is missing, stale, or contradictory, so that I do not mistake plausible prose for a
verified answer.

**Why this priority**: Safe failure is necessary for user trust and makes evaluation of unsupported
questions possible.

**Independent Test**: Submit prepared unsupported, out-of-scope, and contradictory questions and
confirm that ATLAS does not fabricate a definitive answer or citation.

**Acceptance Scenarios**:

1. **Given** no source in the launch corpus supports a principal answer, **When** a visitor submits
   the question, **Then** ATLAS states that it could not verify an answer and identifies the missing
   coverage.
2. **Given** authoritative sources disagree, **When** ATLAS answers, **Then** it presents the
   disagreement with source dates instead of silently choosing one position.
3. **Given** a question is outside the published corpus scope, **When** it is submitted, **Then** the
   visitor receives a scope explanation and a suggestion for a supported question.

### Edge Cases

- The question is empty, excessively long, or contains only punctuation.
- The question asks several unrelated questions in one submission.
- The question uses an alias or spelling variation for a covered technology.
- A source has no publication date or version metadata.
- A previously indexed canonical source is temporarily unavailable.
- A scheduled refresh fails for one collection while previously verified content remains available.
- Multiple retrieved excerpts repeat the same underlying evidence.
- A source excerpt contains instructions directed at an AI system.
- Evidence supports only part of the requested comparison.
- The visitor cancels or repeats a request while the first request is still in progress.
- A retained anonymous request reaches the end of its 30-day retention period while aggregate
  quality metrics still depend on it.
- A visitor reaches the anonymous question limit while another request is still in progress.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a natural-language technical question from an anonymous
  visitor without requiring account creation.
- **FR-002**: The system MUST publish the topics and authoritative documentation, changelog, and
  release-note collections included in the launch corpus.
- **FR-003**: The system MUST distinguish principal factual claims from explanatory or explicitly
  labeled inferential text in an answer.
- **FR-004**: Every principal factual claim MUST reference at least one evidence record, or the
  system MUST omit the claim and explain the evidence gap.
- **FR-005**: Each evidence record MUST expose a source title, publisher, canonical URL, supporting
  excerpt, capture date, and any known publication, version, or release date.
- **FR-006**: Citations MUST navigate from a claim to its evidence record and from the evidence
  record to the original canonical source.
- **FR-007**: The system MUST preserve version, product, date, and comparison constraints stated in
  the visitor's question.
- **FR-008**: The system MUST visibly label inferences and MUST NOT present them as quoted or direct
  source statements.
- **FR-009**: When evidence is insufficient, the system MUST return a structured abstention that
  identifies what could not be verified.
- **FR-010**: When credible sources contradict one another, the system MUST show the disagreement,
  source identity, and relevant date instead of concealing the conflict.
- **FR-011**: The system MUST communicate whether an answer is complete, partial, uncertain, or
  unsupported using text that does not depend on color alone.
- **FR-012**: The system MUST reject invalid questions with a useful correction message and MUST
  preserve the visitor's entered text.
- **FR-013**: The system MUST treat source content as evidence only; instructions embedded inside a
  source MUST NOT change system behavior or authorize an action.
- **FR-014**: The system MUST provide a visible request state and allow the visitor to cancel an
  in-progress answer.
- **FR-015**: Each completed response MUST have a stable identifier that can be associated with
  feedback and quality measurements without exposing private visitor information.
- **FR-016**: Visitors MUST be able to mark a response as useful or not useful and optionally select
  a concise failure category, including incorrect citation.
- **FR-017**: The system MUST allow no more than 10 accepted cited-answer questions per anonymous
  visitor in a rolling 24-hour period and MUST explain when the visitor can try again after reaching
  the limit. Report or document generation does not consume this quota and will use a separate
  policy in its future feature.
- **FR-018**: The system MUST attempt to refresh each launch collection at least once every 24 hours
  and MUST allow an authorized operator to request an additional refresh on demand.
- **FR-019**: A failed refresh MUST NOT replace the last successfully captured source version; the
  system MUST expose the last successful refresh time and the current refresh status.
- **FR-020**: Anonymous questions, generated answers, feedback details, and diagnostic traces MUST
  be stored without directly identifying the visitor and MUST expire 30 days after creation.
- **FR-021**: After anonymous content expires, the system MUST delete the question, answer, detailed
  feedback, and trace content while retaining only non-reversible aggregate quality, latency, error,
  and cost measurements.
- **FR-022**: The system MUST distinguish current documentation from historical changelog and
  release-note evidence and MUST preserve the date and version context of temporal claims.

### Key Entities

- **Question**: A visitor's original text plus any explicit product, version, date, language, or
  comparison constraints.
- **Answer**: The user-visible response, its completion status, principal claims, uncertainty notes,
  and stable response identifier.
- **Claim**: A discrete factual or inferential statement in an answer and its relationship to one or
  more evidence records.
- **Evidence**: A bounded source excerpt with provenance, dates, authority information, and an
  immutable relationship to the captured source version.
- **Source**: A published authoritative collection with canonical identity, ownership, scope, and
  freshness metadata.
- **Citation**: The navigable relationship between a claim and evidence.
- **Feedback**: A visitor's usefulness judgment and optional failure category for a response.

### Scope Boundaries

- The launch corpus contains official documentation, changelogs, and release notes for LangGraph,
  LangChain, and the OpenAI API.
- The feature answers questions from the indexed launch corpus; unrestricted live-web research is
  outside this feature.
- Uploads, private sources, user accounts, saved conversation history, generated reports, broad
  technology comparison matrices, and Spanish localization are outside this feature.
- Generated reports and documents will have a separate usage quota in their future feature; they do
  not count toward the 10-question anonymous cited-answer limit.
- The feature provides technical research support, not legal, medical, financial, or personalized
  high-stakes advice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of 30 prepared in-scope questions receive an answer that addresses the
  requested product, version, and date constraints.
- **SC-002**: At least 95% of audited principal factual claims have citations that directly support
  the claim.
- **SC-003**: At least 90% of prepared unsupported or out-of-scope questions produce an appropriate
  abstention rather than an unsupported definitive answer.
- **SC-004**: Every displayed citation exposes its source identity, canonical link, capture date,
  and supporting excerpt within one user interaction.
- **SC-005**: At least 95% of normal questions show the first useful response content within five
  seconds and complete within fifteen seconds under the published launch limits.
- **SC-006**: All critical flows can be completed using keyboard navigation and remain understandable
  without color cues.
- **SC-007**: At least four of five external test users can ask a supported question, inspect its
  evidence, and correctly identify whether ATLAS verified or abstained without guidance.
- **SC-008**: No prepared source-content instruction changes system behavior or triggers an
  unauthorized action.
- **SC-009**: At least 95% of scheduled corpus refreshes complete successfully during a seven-day
  launch validation period, and every failed refresh preserves the last successful source version.
- **SC-010**: All anonymous content selected in a retention-expiry test is deleted no later than 24
  hours after reaching 30 days of age, while the corresponding aggregate measurements remain usable.
- **SC-011**: At least 90% of 10 prepared temporal questions identify the correct change, chronology,
  or version and cite evidence carrying the relevant date or version context.
- **SC-012**: In every limit-boundary test, the first 10 valid questions are accepted, the next
  question within the same rolling period is rejected before processing, and the visitor sees the
  earliest retry time.

## Assumptions

- The LangGraph, LangChain, and OpenAI documentation, changelog, and release-note collections have
  terms that permit the required retrieval and linking behavior; this assumption MUST be verified
  during planning before ingestion work begins.
- English is the only public interface language for this first vertical slice.
- Visitors have a modern browser and stable internet access.
- Source ingestion occurs before a visitor asks a question; continuous live-web research is a later
  feature.
- A small, versioned evaluation set is an acceptance dependency for this feature, not a future
  enhancement.
- Anonymous usage limits may be conservative during portfolio launch and can change without
  altering the core user journey.
