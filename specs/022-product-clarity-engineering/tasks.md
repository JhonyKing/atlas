# Tasks: Product Clarity and Engineering Portfolio

**Input**: Design documents from `specs/022-product-clarity-engineering/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/public-experience.md

**Tests**: Required because the user requested desktop/mobile visual verification, anonymous public-route verification, accessibility review, SEO inspection, and a hosted configuration fix.

## Phase 1: Setup and Baseline Audit

- [x] T001 Record the baseline Home findings and live canonical/alias header results in `docs/verification/022-product-clarity-engineering.md`
- [x] T002 Preserve baseline 1440×900 and 390×844 Home screenshots under `docs/verification/artifacts/022/baseline/`
- [x] T003 Run SpecKit cross-artifact analysis and resolve critical inconsistencies across `specs/022-product-clarity-engineering/spec.md`, `plan.md`, and `tasks.md`

---

## Phase 2: Foundational P0 Contracts

- [x] T004 Add localized product-home, advanced-option, availability, portfolio, and engineering copy types in `apps/web/src/i18n/index.ts`
- [x] T005 [P] Add failing Home contract and accessibility tests in `apps/web/src/features/home/ProductHome.test.tsx`
- [x] T006 [P] Add failing hosted API availability tests in `apps/web/src/lib/env.test.ts`
- [x] T007 [P] Add failing metadata and robots tests in `apps/web/src/app/metadata.test.ts`
- [x] T008 [P] Add failing anonymous public-route and locale-route coverage in `apps/web/tests/e2e/public-routes.spec.ts`
- [x] T009 [P] Add failing 1440×900 and 390×844 P0 visual assertions plus the ten-capability engineering evidence contract in `apps/web/tests/e2e/product-home.spec.ts`

---

## Phase 3: User Story 1 — Clear Home Experience (P0 / Spec P1)

**Goal**: A first-time visitor understands ATLAS and can start one of three workflows without seeing internal infrastructure language.

**Independent Test**: Home shows the value promise and exactly three actions; automatic sources are the default; manual selection is inside Advanced options; missing hosted API configuration is user-safe.

- [x] T010 [US1] Implement the three-action product introduction in `apps/web/src/features/home/ProductHome.tsx`
- [x] T011 [US1] Replace `AgentWorkspace` composition with `ProductHome` in `apps/web/src/app/page.tsx`
- [x] T012 [US1] Refactor automatic source selection and advanced manual options in `apps/web/src/features/cited-answer/CitedAnswerForm.tsx`
- [x] T013 [US1] Implement typed, non-leaking hosted API availability handling in `apps/web/src/lib/env.ts` and answer API clients
- [x] T014 [US1] Replace documentation-only examples and duplicated evidence copy in `apps/web/src/i18n/index.ts`
- [x] T015 [US1] Add responsive Home/action/disclosure/availability styles in `apps/web/src/app/globals.css`

---

## Phase 4: User Story 2 — Engineering Portfolio (P0 / Spec P2)

**Goal**: Recruiters and engineers can inspect the system depth without adding technical density to Home.

**Independent Test**: `/engineering`, `/en/engineering`, and `/es/engineering` are anonymous, bilingual, evidence-linked, and describe all required capabilities truthfully.

- [x] T016 [P] [US2] Implement evidence-linked engineering content in `apps/web/src/features/engineering/EngineeringPage.tsx`
- [x] T017 [P] [US2] Add unprefixed and localized engineering route wrappers in `apps/web/src/app/engineering/page.tsx` and `apps/web/src/app/[locale]/engineering/page.tsx`
- [x] T018 [US2] Add the engineering navigation destination and locale-preserving link in `apps/web/src/components/layout/AppShell.tsx`
- [x] T019 [US2] Add “Built by Jhonnatan Vazquez — AI Engineer” and GitHub/architecture/case-study links in `apps/web/src/features/home/ProductHome.tsx`
- [x] T020 [US2] Add responsive engineering and portfolio styles in `apps/web/src/app/globals.css`

---

## Phase 5: User Story 3 — Public Discovery and Access (P0 / Spec P3)

**Goal**: Canonical public pages are shareable, indexable, and accessible without a Vercel session.

**Independent Test**: Canonical metadata is present and every public locale route returns a product page without deployment authentication.

- [x] T021 [P] [US3] Add metadata base, canonical, OpenGraph, robots, and improved default SEO in `apps/web/src/app/layout.tsx`
- [x] T022 [P] [US3] Add the indexable public robots policy in `apps/web/src/app/robots.ts`
- [x] T023 [US3] Add route-specific engineering metadata in `apps/web/src/app/engineering/page.tsx` and localized engineering route metadata
- [x] T024 [US3] Extend route matrices with Engineering in `apps/web/tests/e2e/visual-qa-routes.spec.ts` and `apps/web/tests/visual/viewport-matrix.spec.ts`

---

## Phase 6: P0 Verification and Documentation

- [x] T025 Run web lint, strict typecheck, unit tests, production build, and focused browser suites from `apps/web/package.json`
- [x] T026 Capture final 1440×900 and 390×844 Home and Engineering screenshots under `docs/verification/artifacts/022/final/`
- [ ] T027 Verify canonical and alias headers plus anonymous hosted routes and record evidence in `docs/verification/022-product-clarity-engineering.md`
- [x] T028 Update `README.md`, `docs/design/information-architecture.md`, `docs/design/ux-audit.md`, and `docs/architecture/020-ux-ui-brand-redesign.md` from the delivered P0 behavior
- [x] T029 Add Feature 022 status and remaining P1/P2 scope to `docs/product/feature-status-matrix.md` and `docs/product/implementation-status.md`
- [x] T030 Run SpecKit convergence against `specs/022-product-clarity-engineering/` and leave P1/P2 tasks open

---

## Phase 7: P1 — Remaining Public Workflow Clarity

- [ ] T031 [P] Refine plain-language hierarchy and realistic decision examples in `apps/web/src/features/comparison/ComparisonPage.tsx`
- [ ] T032 [P] Refine report entry language, examples, and advanced identifiers in `apps/web/src/features/reports/ReportRequest.tsx`
- [ ] T033 [P] Refine public-benefit copy and empty/error states in `apps/web/src/features/news/DailyNews.tsx`, `apps/web/src/features/corpus/CorpusStatus.tsx`, and `apps/web/src/features/account/AccountPageContent.tsx`
- [ ] T034 Validate P1 public workflows at desktop/mobile and update `docs/verification/022-product-clarity-engineering.md`

---

## Phase 8: P2 — Expanded Portfolio Case Study

- [ ] T035 Create an evidence-backed public case-study presentation in `apps/web/src/features/engineering/CaseStudy.tsx`
- [ ] T036 Add measured portfolio metrics without unsupported claims using `docs/portfolio/kpis.json` and `docs/portfolio/evidence-ledger.json`
- [ ] T037 Add a richer accessible architecture presentation in `apps/web/src/features/engineering/EngineeringPage.tsx`
- [ ] T038 Run an external five-second comprehension review and record results in `docs/portfolio/external-evidence.md`

## Dependencies

- T001–T003 precede code changes.
- T004–T009 precede T010–T024.
- User Story 1 is independently shippable after T010–T015.
- User Story 2 depends only on localized copy foundations and is otherwise parallel with User Story 1.
- User Story 3 can proceed in parallel after metadata tests exist.
- T025–T030 close P0 only. T031–T038 remain explicitly open.

## Parallel Execution Examples

- T005–T009 touch separate test/contract files.
- T016–T017 can proceed while Home work T010–T015 is implemented.
- T021–T022 can proceed while engineering presentation work is implemented.

## Implementation Strategy

1. Preserve the current baseline as evidence.
2. Add failing P0 tests.
3. Deliver the clear Home independently.
4. Deliver the Engineering route independently.
5. Add canonical discovery and anonymous-route proof.
6. Run full verification and documentation closeout.
7. Keep P1/P2 tasks unchecked for subsequent increments.
