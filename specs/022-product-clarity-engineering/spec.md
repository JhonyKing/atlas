# Feature Specification: Product Clarity and Engineering Portfolio

**Feature Branch**: `codex/022-product-clarity-engineering`

**Created**: 2026-08-11

**Status**: Approved for P0 implementation

**Input**: Simplify ATLAS for everyday AI users while preserving technical depth for recruiters and engineers, add an engineering page and portfolio attribution, improve discovery/SEO, and replace hosted configuration errors with user-safe states.

## User Scenarios & Testing

### User Story 1 - Understand and start ATLAS quickly (Priority: P1)

As a person interested in artificial intelligence, I can understand within ten seconds that ATLAS researches AI topics and returns answers I can verify from sources, then start by asking a question, comparing technologies, or creating a report.

**Why this priority**: The current Home asks visitors to understand internal agent infrastructure before they can identify the product's value or primary action.

**Independent Test**: A first-time anonymous visitor can describe the product purpose and select one of the three primary actions from Home without opening technical documentation.

**Acceptance Scenarios**:

1. **Given** an anonymous visitor opens Home, **When** the first viewport is displayed, **Then** the visitor sees the verifiable-answer promise, a short explanation, and actions to ask, compare, or create a report.
2. **Given** the visitor chooses to ask a question, **When** the question experience is shown, **Then** ATLAS selects relevant verified sources automatically by default.
3. **Given** the visitor wants manual control, **When** advanced options are expanded, **Then** a source collection can be selected without exposing internal terminology in the default flow.
4. **Given** the public API is not configured or reachable, **When** the visitor attempts research, **Then** ATLAS presents a localized, user-safe availability message and never exposes environment-variable names or internal deployment instructions.

---

### User Story 2 - Inspect the engineering depth (Priority: P2)

As a recruiter or engineer, I can open a dedicated engineering page that explains the implemented RAG, agent orchestration, retrieval, claim verification, citations, structured outputs, persistence, evaluations, observability, and architecture with links to evidence.

**Why this priority**: Simplifying Home must not hide the technical work that makes ATLAS a strong AI Engineer portfolio project.

**Independent Test**: An anonymous visitor can open the engineering page from the public interface and follow links to the repository, architecture record, and case-study evidence.

**Acceptance Scenarios**:

1. **Given** an anonymous visitor opens the engineering page, **When** the page loads, **Then** the visitor sees the system flow, major engineering capabilities, and explicit evidence/limitation language.
2. **Given** a visitor reaches the portfolio attribution, **When** links are selected, **Then** GitHub, architecture, and case-study destinations are valid and clearly labeled.
3. **Given** a Spanish-localized route, **When** the visitor opens engineering, **Then** the page preserves the selected language and the same factual architecture claims.

---

### User Story 3 - Discover and access public routes safely (Priority: P3)

As an anonymous visitor or search engine, I can access every public ATLAS route without a Vercel session and receive accurate page metadata from the canonical production domain.

**Why this priority**: A portfolio product must be shareable, discoverable, and explicit about which deployment URL is canonical.

**Independent Test**: An unauthenticated browser receives successful public pages, canonical metadata, and indexable responses on the production domain while non-canonical deployment aliases do not become competing search results.

**Acceptance Scenarios**:

1. **Given** an unauthenticated browser, **When** each public English and Spanish route is opened, **Then** no Vercel login or deployment-protection page is shown.
2. **Given** a crawler opens the canonical production Home or engineering page, **When** metadata is inspected, **Then** the title, description, canonical URL, OpenGraph data, and indexing directive describe the public product accurately.
3. **Given** a crawler follows a non-canonical Vercel team alias, **When** the response redirects, **Then** the canonical production domain remains the single indexable destination.

### Edge Cases

- JavaScript is disabled or hydration has not completed: the core value proposition, three actions, portfolio attribution, and engineering explanation remain readable.
- The agent tool catalog is unavailable: Home remains usable for navigation and does not display a permanent loading card as the product introduction.
- The public API origin is missing: forms do not leak `NEXT_PUBLIC_API_ORIGIN` and communicate that live research is temporarily unavailable.
- A locale-prefixed equivalent is not implemented: language switching must not produce a 404.
- Long translated text and 390-pixel mobile screens must not overflow or hide the primary action.
- Technical evidence links that are repository documents must clearly identify that they open external project documentation.

## Requirements

### Functional Requirements

- **FR-001**: Home MUST communicate that ATLAS researches AI topics and produces source-verifiable answers within the first visible product section.
- **FR-002**: Home MUST present exactly three primary product actions: ask a question, compare AI technologies, and create a report.
- **FR-003**: Home MUST make asking a question the primary in-page workflow and link the other actions to their dedicated routes.
- **FR-004**: The default question workflow MUST select relevant verified sources automatically.
- **FR-005**: Manual source selection MUST remain available within a collapsed advanced-options control.
- **FR-006**: Default public copy MUST avoid internal implementation terms including typed tools, budgets, approval rules, corpus, and evidence state.
- **FR-007**: Evidence MUST be described as a user benefit: inspectable sources, dates, and citations.
- **FR-008**: Example prompts MUST represent realistic AI engineering decisions, comparisons, architecture choices, and operational trade-offs.
- **FR-009**: The interface MUST contain one visible language control and preserve the current route when switching language.
- **FR-010**: Home MUST include the attribution “Built by Jhonnatan Vazquez — AI Engineer” with clearly labeled GitHub, architecture, and case-study links.
- **FR-011**: A public engineering page MUST explain RAG, agents, retrieval, claim verification, citations, structured outputs, persistence, evaluations, observability, and the architecture flow without overstating unverified production claims.
- **FR-012**: Missing or invalid hosted API configuration MUST be represented as a localized product availability state; internal variable names MUST NOT be rendered to visitors.
- **FR-013**: Public pages MUST provide accurate title, description, canonical, OpenGraph, and robots metadata.
- **FR-014**: The canonical production domain MUST be `https://atlasai-lilac.vercel.app` unless the owner later approves a custom domain.
- **FR-015**: Every public English and Spanish route MUST be accessible without a Vercel session.
- **FR-016**: P0 changes MUST preserve the existing answer, comparison, report, news, source, account, admin, API, evidence, and locale contracts.
- **FR-017**: Desktop at 1440×900 and mobile at 390×844 MUST have no horizontal overflow, clipped actions, duplicate locale controls, or unreadable primary copy.
- **FR-018**: P1 and P2 improvements MUST remain explicit follow-up work and MUST NOT be silently marked complete with P0.

### Key Entities

- **Primary Action**: A user-facing choice with a localized label, short benefit statement, destination, and one designated default action.
- **Advanced Research Options**: A collapsed control that contains optional manual source selection while automatic selection remains the default.
- **Engineering Capability**: A factual portfolio claim with a plain-language explanation, implementation boundary, evidence link, and limitation where relevant.
- **Public Route Evidence**: A recorded route, locale, status, anonymous-access result, metadata result, viewport result, and verification timestamp.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In a five-second first-viewport review, the product name, AI research purpose, verifiable-source benefit, and primary action are all visible at 1440×900 and 390×844.
- **SC-002**: The default Home contains zero visible occurrences of typed tools, budgets, approval rules, corpus, evidence state, or environment-variable names.
- **SC-003**: A visitor can start asking a question in one interaction and reach comparison or reports in one interaction from the action selector.
- **SC-004**: All public English and Spanish routes return successful pages without a Vercel authentication screen.
- **SC-005**: The canonical Home and engineering page expose complete title, description, canonical, OpenGraph, and indexable robots metadata.
- **SC-006**: Automated viewport checks report zero horizontal overflow and all visible interactive targets are at least 40 by 40 pixels at 1440×900 and 390×844.
- **SC-007**: Existing frontend unit tests, type checks, lint, build, and public-route browser tests pass without changing backend contracts.
- **SC-008**: The engineering page links at least ten technical capabilities to truthful project evidence or an explicit limitation.

## Assumptions

- The current canonical public domain remains `https://atlasai-lilac.vercel.app` for this slice.
- GitHub links use the public `JhonyKing/atlas` repository.
- Existing repository architecture and verification documents are the case-study evidence; no unsupported marketing claims will be invented.
- The managed public API may still be unavailable during P0. The frontend will handle this honestly; configuring a real API URL remains a deployment task rather than a visual workaround.
- This feature changes presentation and public metadata, not agent, retrieval, storage, report, or authorization behavior.

## Scope by Delivery Priority

- **P0**: Home clarity, progressive disclosure, automatic source default, portfolio attribution, engineering page, safe hosted-API state, canonical/SEO/robots, anonymous route and desktop/mobile verification.
- **P1**: Plain-language and hierarchy refinement across Compare, Reports, News, Sources, and Account, plus route-specific realistic examples and state copy.
- **P2**: Expanded visual case study, narrated portfolio metrics, richer architecture presentation, and further polish informed by external usability review.
