# Feature Specification: ATLAS UX/UI and Brand Redesign

**Feature Branch**: `020-ux-ui-brand-redesign`

**Created**: 2026-08-07

**Status**: Draft

**Input**: Product-design brief for an evidence-first research interface with a coherent information architecture, ATLAS brand system, responsive accessibility, and route-based workflows.

## User Scenarios & Testing

### User Story 1 - Understand and enter the product quickly (Priority: P1)

As a new visitor, I want to understand in under ten seconds that ATLAS is evidence-first technical research and know where to ask a question, so the product feels like a professional research tool rather than a collection of demo panels.

**Why this priority**: Ask ATLAS is the flagship journey and the first portfolio impression.

**Independent Test**: Open the home route at desktop and mobile widths, identify the primary action without scrolling, switch locale, and verify heading, supporting copy, navigation, focus state, and empty/error state.

**Acceptance Scenarios**:

1. **Given** a clean browser, **When** the visitor opens `/`, `/en`, or `/es`, **Then** a branded AppShell and Ask ATLAS hero appear with one clear primary research action.
2. **Given** the visitor chooses Spanish, **When** the home route renders, **Then** navigation, heading, form labels, helper text, progress, errors, and evidence states use the Spanish catalog without changing API contracts.
3. **Given** a keyboard-only visitor, **When** they navigate the shell and ask form, **Then** focus is visible, order is logical, controls have accessible names, and no interaction depends on color alone.

### User Story 2 - Navigate distinct research workflows (Priority: P1)

As a researcher, I want Ask, Compare, Reports, News, Sources, Account, and Admin to have clear destinations and navigation, so public research, personal data, and internal operations are not mixed on one long page.

**Why this priority**: Information architecture is the central usability correction in the design brief.

**Independent Test**: Visit every public and admin route at desktop/mobile widths, use primary navigation and back links, and verify the correct feature is rendered without duplicating or exposing unrelated controls.

**Acceptance Scenarios**:

1. **Given** the public AppShell, **When** a user selects Ask, Compare, Reports, News, Sources, or Account, **Then** the URL and page content match the selected workflow and the active item is announced accessibly.
2. **Given** an operator, **When** they visit `/admin`, **Then** governance and human review are available in a denser operations layout and are absent from the public homepage.
3. **Given** a mobile viewport, **When** the user opens navigation, **Then** the mark is used appropriately, navigation is keyboard/touch accessible, and the page has no horizontal overflow.

### User Story 3 - Trust evidence and results (Priority: P1)

As a technical researcher, I want answers, citations, comparison cells, source status, and loading/error states to have a consistent visual language, so I can distinguish supported, partial, unsupported, and unavailable evidence without reading raw JSON.

**Why this priority**: Evidence is ATLAS's product differentiator and must be readable, not decorative.

**Independent Test**: Exercise complete, partial, unsupported, contradictory, loading, error, and empty fixtures across answer, comparison, sources, news, and reports; verify labels, icons/text, metadata, links, focus, and responsive layout.

**Acceptance Scenarios**:

1. **Given** a cited answer, **When** it completes, **Then** the UI separates answer, claims, evidence summary, citation metadata, and limitations with inspectable source links.
2. **Given** a comparison matrix, **When** a cell is supported, partial, unsupported, or contradictory, **Then** the state includes a text label and accessible indicator and does not rely only on saturated background color.
3. **Given** a long-running request, **When** progress events arrive, **Then** the interface displays only real backend stages with a readable research timeline and truthful retry/cancel behavior.

### User Story 4 - Use a coherent brand and component system (Priority: P2)

As a product owner, I want the approved ATLAS mark, wordmark, palette, typography, spacing, form controls, buttons, and surfaces to be reusable tokens/components, so later features look intentional and consistent.

**Why this priority**: Shared foundations reduce visual drift while allowing vertical slices to be implemented safely.

**Independent Test**: Render brand assets and core components on light surfaces at required sizes and states; inspect SVG scaling, contrast, focus, disabled/loading/error/success variants, and absence of repeated ad-hoc color values.

**Acceptance Scenarios**:

1. **Given** the approved transparent PNG references, **When** the web assets are generated, **Then** stacked, horizontal, mark, favicon, and optional app icons are available as clean web-ready assets without embedded PNGs in SVG.
2. **Given** the light design system, **When** a component renders, **Then** it uses centralized tokens for brand, surface, text, semantic evidence, spacing, radius, and shadow.
3. **Given** an input or button state, **When** it is hovered, focused, active, disabled, loading, errored, or successful, **Then** the state is visually and semantically distinguishable and touch targets remain usable.

### User Story 5 - Review responsive and accessible quality (Priority: P2)

As a reviewer, I want visual and accessibility evidence at the specified breakpoints, so a passing build is not mistaken for a usable product.

**Why this priority**: The brief explicitly requires Playwright visual QA and responsive/accessibility checks.

**Independent Test**: Capture screenshots and run browser checks at 375/390/768/1024/1280/1440/1920 widths, including 1440×900 and 390×844 evidence, and inspect overflow, contrast, semantics, reduced motion, and route reachability.

**Acceptance Scenarios**:

1. **Given** any required viewport, **When** each public route renders, **Then** content stays within the viewport, tables have a responsive strategy, and forms remain usable with touch.
2. **Given** reduced-motion preference, **When** loading/progress transitions render, **Then** motion is reduced without hiding status.
3. **Given** a production build, **When** the visual and accessibility QA suite runs, **Then** it reports route, screenshot, overflow, logo rendering, focus, and semantic failures as actionable artifacts.

## Edge Cases

- A logo reference contains a transparent background, glow, or raster artifact; web assets must preserve the symbol while avoiding a screenshot-like background.
- The SVG logo is placed on a light surface or a future dark surface; the mark remains legible and does not require a gray rectangle.
- A source is stale, unsupported, unavailable, or has no evidence; status text and explanation remain explicit and are not conveyed by color alone.
- The API is unavailable on a route; the page explains the affected workflow and offers retry where safe instead of showing a raw 500.
- A report has no completed source comparison; the primary Reports UX offers a guided empty state and keeps manual ID entry secondary.
- A user lacks authentication for Account/private resources; the page explains optional login and does not expose another user's data.
- An operator opens an admin route without permission; the route fails closed and does not leak governance/review data.
- A Spanish string is longer than its English equivalent; controls, navigation, tables, and cards do not clip or overflow.
- A comparator matrix is wider than a mobile viewport; it remains readable with an explicit responsive pattern rather than accidental horizontal overflow.
- A browser has no network connection or an in-flight request is cancelled; progress and error states preserve context and allow safe retry.

## Requirements

### Functional Requirements

- **FR-001**: The frontend MUST provide a route-based information architecture for `/`, `/compare`, `/reports`, `/news`, `/sources`, `/account`, `/admin`, `/admin/sources`, `/admin/reviews`, and `/admin/governance` without changing backend API contracts.
- **FR-002**: The frontend MUST provide a shared AppShell with responsive navigation, active state, keyboard access, focus visibility, route-aware locale switching, horizontal logo on desktop, and mark on mobile.
- **FR-003**: The home route MUST prioritize Ask ATLAS above the fold with the approved promise, concise supporting copy, technical question form, source selector, primary action, and clear supported-source/trust explanation.
- **FR-004**: The frontend MUST centralize brand/design tokens for the approved navy, indigo, electric blue, cyan, teal, amber, light surfaces, borders, text, semantic evidence states, gradient, spacing, radius, shadow, typography, and focus treatment.
- **FR-005**: The frontend MUST provide web-ready stacked, horizontal, mark, favicon, and optional app icon assets based on the inspected canonical references; SVG MUST be primary where feasible and MUST NOT embed PNGs.
- **FR-006**: The frontend MUST provide reusable accessible components for Button, Input, Textarea, Select, Checkbox, FileUpload, Field, Label, HelperText, ErrorMessage, status badge, evidence state, citation card, and research progress.
- **FR-007**: The answer experience MUST present query, progress, answer, claims, citations, evidence state, source metadata, limitations, and inspectable links in a readable research layout rather than raw JSON.
- **FR-008**: The comparator route MUST present technology chips/selection, criteria controls, progress, a readable evidence matrix, responsive behavior, and inspectable cells for supported/partial/unsupported/contradictory states.
- **FR-009**: The Reports route MUST guide users from completed research/comparison cards to PDF/DOCX generation, keep manual source-ID entry secondary, and expose artifact status/download/delete states.
- **FR-010**: The News route MUST present the previous-day internet signal as an editorial module with date, title, summary, publisher, evidence/source link, and truthful unavailable/no-evidence states.
- **FR-011**: The Sources route MUST present collection publisher, counts, freshness, canonical root, verification state, and an explanation for stale/unavailable status with clear information hierarchy.
- **FR-012**: The Account route MUST contain optional login, validation/loading/error/signed-in states, and private resources behind the existing auth/ownership contracts; authentication behavior MUST NOT be reimplemented in the frontend.
- **FR-013**: Admin routes MUST contain corpus governance, human review, and internal operations in an operations-oriented layout and MUST NOT appear as public homepage panels.
- **FR-014**: The frontend MUST implement responsive/accessibility QA at 375, 390, 768, 1024, 1280, 1440, and 1920 widths, including 1440×900 and 390×844 screenshots, keyboard/focus, semantic labels, contrast, reduced motion, route checks, and overflow checks.
- **FR-015**: The frontend MUST preserve existing SSE, evidence behavior, unsupported states, API contracts, model behavior, persistence, and generated artifact links; this feature MUST remain frontend/product-design scope.
- **FR-016**: The design documentation MUST include UX audit, information architecture, design system, brand guidelines, planned file changes, asset inventory, and visual QA evidence before the feature is closed.

### Key Entities

- **AppShell**: Shared navigation, logo, locale control, content frame, responsive behavior, and route context.
- **BrandAsset**: Stacked logo, horizontal logo, mark, favicon, and optional app icon with source/reference, dimensions, transparency, and allowed usage.
- **DesignToken**: Centralized color, type, spacing, radius, shadow, motion, and focus values.
- **EvidenceState**: Supported/verified, partial, unsupported, contradictory, information, stale, unavailable, and loading representation with label/icon/text.
- **ResearchSurface**: A route-level user journey for ask, compare, reports, news, sources, account, or admin.
- **VisualQAArtifact**: Screenshot/check result tied to route, viewport, commit, and observed findings.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A new visitor can identify what ATLAS does and the primary Ask action within ten seconds on desktop and mobile home screenshots.
- **SC-002**: Every required route is reachable from the AppShell or a documented secondary navigation path, and no public home screenshot contains admin-only panels.
- **SC-003**: 100% of representative evidence states include a visible text label, accessible semantic status, and explanatory copy where needed; no state is color-only.
- **SC-004**: The design token audit finds no new repeated brand hex values outside token/asset definitions in the redesigned frontend files.
- **SC-005**: All specified viewport checks pass without accidental horizontal overflow; comparator/report layouts remain usable at 390px width.
- **SC-006**: Keyboard and semantic accessibility checks pass for AppShell, primary forms, navigation, status/progress, evidence/citation controls, and approval/error states.
- **SC-007**: Visual QA artifacts exist for 1440×900 and 390×844 after each vertical slice, with findings resolved or explicitly recorded before the next slice.
- **SC-008**: The approved logo assets render crisply in stacked, horizontal, mark, and favicon usage on light surfaces, with no embedded PNG in the SVG files.
- **SC-009**: Existing frontend unit/E2E tests and backend contracts remain green; no backend file or API contract changes are required for the redesign.

## Scope Boundaries

- This feature is frontend/product design only. It MUST NOT change backend APIs, SSE, models, persistence, evidence semantics, generated-document behavior, or provider logic.
- The first phase is documentation and inspection: no broad page rewrite starts until UX audit, information architecture, design system, brand guidelines, asset inventory, and planned-file list exist.
- Light mode is the priority. Dark mode may receive token-compatible preparation but is not a delivery requirement.
- Existing PNG references are canonical visual references, not automatically production assets; SVG recreation must preserve the approved symbol without embedding raster data.
- Routes may initially use existing backend clients and feature components; refactoring is allowed only when it preserves behavior and reduces UX/layout debt.

## Assumptions

- The three PNGs in `imgs/` are the approved reference set: stacked, horizontal, and mark compositions.
- Inter/system sans-serif is acceptable because the project already uses an Inter/system stack and no remote font dependency is required.
- `/en` and `/es` remain the user-facing locale URL segments while `en-US`/`es-MX` remain internal locale contracts.
- Admin authentication/authorization is provided by existing backend contracts; the redesign will not invent client-side permission logic.
- Playwright is available for visual QA; screenshots and reports are retained as evidence under a documented results path.
