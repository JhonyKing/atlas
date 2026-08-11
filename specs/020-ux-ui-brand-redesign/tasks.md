# Tasks: ATLAS UX/UI and Brand Redesign

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/)

**Prerequisites**: Feature 019 agent slice remains green; no task below changes backend/API/SSE/evidence contracts.

## Phase 1: Inspection and design foundation (P1, no broad UI coding)

- [X] T001 [US1] Inventory all `apps/web` routes, feature components, API clients, locale catalogs, styles, tests, and current user journeys in `docs/design/ux-audit.md`.
- [X] T002 [US4] Inspect every file under `imgs/`, record filename, dimensions, format, alpha/transparency, visual role, and canonical composition in `docs/design/brand-guidelines.md`.
- [X] T003 [US2] Define route ownership, public/admin separation, navigation hierarchy, locale behavior, and migration approach in `docs/design/information-architecture.md`.
- [X] T004 [US4] Define the light-first token system, evidence semantic states, type/spacing/radius/shadow/motion rules, and component states in `docs/design/design-system.md`.
- [X] T005 [US4] Document logo meaning, stacked/horizontal/mark usage, clear space, minimum size, backgrounds, palette, gradient, typography, favicon use, and incorrect usage in `docs/design/brand-guidelines.md`.
- [X] T006 [US1] Record the planned files, backend-scope boundary, strengths, high-priority UX findings, and Definition-of-Ready review in `docs/design/ux-audit.md`.
- [X] T007 [US1] Review Phase 1 artifacts against the brief and record owner approval or findings before broad frontend implementation in `docs/verification/020-ux-ui-phase-1-review.md`. Evidence: review approved the brand-assets slice and preserved the backend scope guard.

## Phase 2: Brand assets (P1)

- [X] T008 [P] [US4] Recreate the approved futuristic A mark as clean path/polygon/line/circle SVG without embedded PNG in `apps/web/public/brand/atlas-mark.svg`. Evidence: `docs/verification/020-brand-assets.md` and visual screenshots.
- [X] T009 [P] [US4] Create stacked and horizontal SVG compositions from the approved mark/wordmark in `apps/web/public/brand/atlas-logo-stacked.svg` and `apps/web/public/brand/atlas-logo-horizontal.svg`. Evidence: `docs/verification/020-brand-assets.md`.
- [X] T010 [P] [US4] Generate transparent PNG fallbacks, favicon, and optional app icons from the approved SVG assets in `apps/web/public/brand/`. Evidence: reproducible Playwright generator, metadata wiring, and dimension tests in `apps/web/src/brand-assets.test.ts`.
- [X] T011 [US4] Add asset rendering/transparent-background/minimum-size tests and document output dimensions in `apps/web/src/brand-assets.test.ts` and `docs/verification/020-brand-assets.md`. Evidence: 4 new Vitest checks passed; Playwright screenshots reviewed.

## Phase 3: Tokens and shared components (P1)

- [X] T012 [US4] Replace repeated global color/surface/text/radius/spacing/shadow/focus values with centralized ATLAS tokens in `apps/web/src/app/globals.css` or `apps/web/src/styles/tokens.css`. Evidence: tokens and semantic evidence colors are defined in `globals.css`.
- [X] T013 [P] [US4] Add shared brand components for logo/wordmark/mark usage in `apps/web/src/components/brand/AtlasLogo.tsx`. Evidence: reusable stacked, horizontal, and mark variants reference the approved SVG assets.
- [X] T014 [P] [US4] Add accessible Button, Input, Textarea, Select, Checkbox, Field, Label, HelperText, ErrorMessage, and FileUpload primitives in `apps/web/src/components/forms/`. Evidence: shared primitives expose labels, helper/error associations, focusable controls, loading, disabled, and danger states.
- [X] T015 [P] [US3] Add semantic evidence state/badge, citation card, source metadata, and research progress components in `apps/web/src/components/evidence/` and `apps/web/src/components/research/`. Evidence: status labels/icons and bounded citation/progress primitives are covered by component tests.
- [X] T016 [US4] Add component unit tests for keyboard/focus/loading/error/success/disabled states and evidence labels in `apps/web/src/components/**/__tests__/`. Evidence: `apps/web/src/components/components.test.tsx` covers brand, form, evidence, citation, and progress semantics.

## Phase 4: AppShell and information architecture (P1)

- [X] T017 [US2] Implement responsive AppShell with horizontal desktop logo, mobile mark, public navigation, locale switch, active state, and content frame in `apps/web/src/components/layout/AppShell.tsx` and `apps/web/src/components/layout/Navigation.tsx`. Evidence: desktop/mobile Playwright screenshots and mobile menu `aria-expanded` check.
- [X] T018 [US2] Integrate AppShell in `apps/web/src/app/layout.tsx` without changing locale provider/API behavior; add route-level metadata and skip-link semantics. Evidence: TypeScript/ESLint pass and route smoke.
- [X] T019 [US2] Create locale-aware route pages for `/reports`, `/news`, `/sources`, `/account`, `/admin`, `/admin/sources`, `/admin/reviews`, and `/admin/governance` in `apps/web/src/app/[locale]/`. Evidence: route surfaces resolve with HTTP 200 in Playwright smoke.
- [X] T020 [US2] Add route/navigation smoke tests for public/admin separation, active state, locale paths, and no unrelated home panels in `apps/web/tests/e2e/app-shell.spec.ts`. Evidence: Playwright checks cover route status, active nav, locale targets, skip-link semantics, mobile menu, and public-home content separation; authenticated admin authorization remains a backend/operations concern for T033.
- [X] T021 [US2] Move existing News, Corpus, Auth/private, Governance, Review, and Reports feature components behind their route owners while retaining backend clients and compatibility links. Evidence: homepage now owns only the Ask/agent journey; feature routes and localized equivalents resolve independently, and Playwright asserts the public home has no corpus/news/auth/report/admin panels.

## Phase 5: Ask ATLAS and evidence experience (P1)

- [X] T022 [US1] Redesign the home hero and question form around the ATLAS promise, source selector, supported-source explanation, examples/empty state, and one primary action in `apps/web/src/features/cited-answer/CitedAnswerForm.tsx` and focused components. Evidence: Ask hero, trust copy, source selector, example buttons, and primary action are covered by `docs/verification/020-ask-evidence.md`.
- [X] T023 [US3] Refactor answer progress, claims, citations, limitations, feedback, and abstention into readable research surfaces using shared evidence/citation components without changing SSE behavior. Evidence: existing answer/abstention tests remain green; SSE stages feed `ResearchProgress` and citations use `CitationCard`.
- [X] T024 [US3] Add evidence state labels/icons/tooltips and citation inspection affordances with accessible semantics in `apps/web/src/features/evidence/`. Evidence: `EvidenceStatus` exposes text/icon state and `CitationCard` preserves bounded excerpt, metadata, and canonical link.
- [X] T025 [US1] Add Ask route responsive/accessibility tests and Playwright visual QA at 1440×900 and 390×844; save artifacts under `test-results/` and `docs/verification/`. Evidence: `apps/web/tests/e2e/ask.spec.ts` passed 2/2 and saved desktop/mobile screenshots.

## Phase 6: Comparator (P1)

- [X] T026 [US3] Redesign technology/criteria controls as accessible chips/fields with clear selected/available states in `apps/web/src/features/comparison/ComparisonPage.tsx`. Evidence: keyboard-focusable chips expose selected/available state, enforce the 2–4 technology bound, and retain native checkbox semantics.
- [X] T027 [US3] Redesign comparison progress and matrix readability, evidence links, supported/partial/unsupported/contradictory states, and responsive overflow strategy in `apps/web/src/features/comparison/`. Evidence: matrix state legend, text/icon status labels, inspectable evidence IDs, cell explanations, sticky headers, and keyboard-focusable horizontal region.
- [X] T028 [US3] Add comparator responsive/accessibility tests and visual QA at 1440×900 and 390×844 without changing comparison API/SSE contracts. Evidence: existing route tests plus mocked SSE matrix-state journey and desktop/mobile screenshots.

## Phase 7: Reports, News, Sources, Account, Admin (P2)

- [X] T029 [US2] Redesign `/reports` around recent completed research/comparison cards, guided PDF/DOCX generation, artifact states, and secondary manual/advanced ID mode in `apps/web/src/features/reports/`. Evidence: guided two-step surface with bounded empty state and manual ID contract.
- [X] T030 [US2] Redesign `/news` as an editorial Internet Signal surface with date, title, summary, publisher, source link, and unavailable/no-evidence explanation in `apps/web/src/features/news/`. Evidence: ready/loading/unavailable states with score, corroboration, attribution, and reason-specific copy.
- [X] T031 [US2] Redesign `/sources` collection cards with counts, publisher, freshness, stale explanation, canonical root, and semantic status in `apps/web/src/features/corpus/CorpusStatus.tsx`. Evidence: semantic collection cards and freshness/count definition lists.
- [X] T032 [US2] Redesign `/account` auth/private resource forms with labels, helper/error/loading/signed-in states and ownership-safe empty states in `apps/web/src/features/auth/` and `apps/web/src/features/private-data/`. Evidence: accessible fields, busy/error handling, upload validation state, and anonymous ownership-safe resource empty state.
- [X] T033 [US2] Redesign `/admin` and subroutes for governance/review/internal operations with denser utility layout and no public-home leakage in `apps/web/src/features/corpus/GovernancePanel.tsx` and `apps/web/src/features/agent/ReviewPanel.tsx`. Evidence: retryable governance metrics, labelled review fields, busy/error/decision states, and utility cards isolated from public routes.
- [X] T034 [US2] Add route-level empty/error/retry and visual QA artifacts for reports, news, sources, account, and admin at desktop/mobile widths. Evidence: `apps/web/tests/e2e/route-states.spec.ts` covers bounded empty/error/retry states at both target viewports.

## Phase 8: Responsive, accessibility, and final visual QA (P2)

- [X] T035 [US5] Add Playwright viewport matrix for 375, 390, 768, 1024, 1280, 1440, and 1920 widths, including screenshots at 1440×900 and 390×844 in `apps/web/playwright.config.ts` and `apps/web/tests/visual/`. Evidence: `apps/web/tests/visual/viewport-matrix.spec.ts`.
- [X] T036 [US5] Add automated checks for horizontal overflow, focus order/visibility, semantic labels, contrast, reduced motion, touch targets, route reachability, favicon, and SVG rendering in `apps/web/tests/visual/`. Evidence: the viewport matrix asserts all listed checks for representative public/admin routes.
- [X] T037 [US5] Run a second visual-only design pass across all routes; record findings/resolutions without adding new product features in `docs/verification/020-final-visual-review.md`. Evidence: 60/60 bilingual route screenshots and documented harness/layout fixes.
- [X] T038 [US5] Run production build and inspect responsive screenshots for layout shift, asset loading, and route errors; retain evidence under `test-results/`. Evidence: `docs/verification/020-production-build.md`, production build and 49/49 viewport matrix.

## Phase 9: Documentation, convergence, and closeout

- [X] T039 [P] Update `README.md` with route map, design system, brand asset usage, UX evidence, and visual QA links. Evidence: Feature 020 section in `README.md`.
- [X] T040 [P] Add/update the UX/architecture ADR in `docs/adr/` for route separation, AppShell, tokens, and brand assets. Evidence: `docs/adr/0016-ux-ui-brand-redesign.md` and `docs/architecture/020-ux-ui-brand-redesign.md`.
- [X] T041 [P] Update `docs/product/feature-status-matrix.md` and PRD traceability with Feature 020 and implementation/evidence status. Evidence: Feature 020 status row and UX/UI traceability addendum.
- [X] T042 Run Speckit analyze after task generation and resolve critical contradictions before implementation. Evidence: `docs/verification/020-speckit-analysis.md`; no critical findings remain.
- [X] T043 Run full frontend lint/typecheck/unit/E2E plus existing backend regression checks to prove no backend behavior changed. Evidence: `docs/verification/020-production-build.md`; latest regression is frontend unit 35/35, Playwright 150 passed/6 hosted-only skips, backend 428 passed/4 skipped, with build/lint/typecheck/mypy passed.
- [X] T044 Run Speckit converge after implementation; keep Feature 020 open while visual QA, accessibility, route, or documentation gates remain pending. Evidence: convergence checked the 16 FRs, 9 buildable SCs, plan decisions, constitution, code scope, and all 45 tasks; no actionable findings and no convergence tasks appended.
- [X] T045 Commit each vertical slice with README/ADR/evidence updates and task/route traceability. Evidence: vertical commits were pushed on `codex/018-production-deployment`; this closeout commit includes the final regression, convergence, documentation, and task traceability updates.

## Dependencies & Execution Order

- T001-T006 are complete inspection/design artifacts; T007 is the review checkpoint and blocks broad UI coding.
- T008-T011 brand assets block AppShell/logo integration.
- T012-T016 tokens/components block AppShell and feature redesigns.
- T017-T021 AppShell/routes block route-specific UX slices.
- T022-T025 Ask/evidence is the first user-facing MVP slice; T026-T028 comparator follows.
- T029-T034 cover remaining public/admin surfaces and depend on AppShell/tokens.
- T035-T038 depend on all desired route slices and block closeout.
- T039-T045 are required for Definition of Done.

## Definition of Done

Feature 020 is complete only when audit/design docs are current, approved assets are web-ready, tokens
and shared components are used, route information architecture is implemented, all required workflows
have clear responsive/accessibility states, screenshots and QA artifacts exist at required widths,
existing backend behavior/tests remain green, and README/ADR/status documentation reflects the actual
frontend. A CSS-only polish or a passing build alone does not close the feature.
