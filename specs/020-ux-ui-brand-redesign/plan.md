# Implementation Plan: ATLAS UX/UI and Brand Redesign

**Branch**: `020-ux-ui-brand-redesign` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

## Summary

Reframe the existing frontend as a coherent evidence-first research product. The implementation
starts with inspection/audit artifacts (already produced for this feature), then proceeds through
brand assets, design tokens, AppShell/route boundaries, Ask/evidence, Compare, Reports, News,
Sources, Account, Admin, responsive/accessibility polish, and visual QA. Existing backend/API/SSE/
evidence behavior remains unchanged.

## Technical Context

**Language/Version**: TypeScript strict, React/Next.js App Router, CSS custom properties, SVG

**Primary Dependencies**: Existing Next.js, React, locale provider, feature API clients, Vitest,
Playwright; no new design framework unless a concrete gap is demonstrated

**Storage**: N/A for design; existing report/private/evidence storage contracts are preserved

**Testing**: ESLint, TypeScript, Vitest, Playwright route/E2E, screenshot visual QA, accessibility
and overflow checks

**Target Platform**: Responsive web, light-first, future-dark-compatible tokens

**Project Type**: Next.js web application with route-level research workflows

**Performance Goals**: No unnecessary remote font/assets; preserve existing streaming behavior and
avoid layout shift from branding/navigation; route builds remain bounded

**Constraints**: No backend/API/contract/persistence/provider changes; no broad rewrite before audit
docs; approved assets are canonical references; no decorative gradients/glow overload; use Node 24
toolchain; retain existing behavior/tests

**Scale/Scope**: Public portfolio beta routes plus restricted admin routes at seven required widths

## Constitution Check

- Evidence Over Fluency: PASS - evidence states and citations become clearer without changing their semantics.
- Spec Before Code: PASS - audit, IA, design system, brand guidelines, plan, contracts, and tasks precede broad UI work.
- Test and Evaluate First: PASS - existing tests plus route/visual/accessibility gates are required after each slice.
- Explicit Contracts and Type Safety: PASS - existing API/SSE/evidence contracts remain unchanged; new UI props remain typed.
- Provider Independence with Measured Routing: PASS - no provider/model changes.
- Security and Privacy by Design: PASS - account/private/admin routes retain backend authorization; no new client secrets.
- Observable and Cost-Aware: PASS - no backend observability changes; visual QA artifacts identify route/revision/browser.
- Small Vertical Slices Before Scale: PASS - ordered design slices and per-slice QA.
- English-Canonical Engineering: PASS - code/tokens/docs are English; user-facing locale catalogs remain bilingual.

## Project Structure

```text
specs/020-ux-ui-brand-redesign/       # feature decision record
docs/design/                          # audit, IA, tokens, brand guidance
apps/web/public/brand/                # SVG/PNG/favicon assets
apps/web/src/components/              # brand/layout/navigation/form/evidence primitives
apps/web/src/app/[locale]/            # route-level research/account/admin surfaces
apps/web/src/features/                # existing API-connected feature journeys
apps/web/tests/                       # route, accessibility, visual smoke coverage
test-results/                         # visual QA artifacts (redacted and reviewable)
```

**Structure Decision**: Keep feature-domain logic in existing feature folders and add shared
presentation primitives under `src/components`. Use the App Router for information architecture;
do not introduce a second CSS framework or duplicate API clients.

## Implementation Sequence

1. Phase 0 (complete before coding): inspect frontend/assets, write audit/IA/design-system/brand
   docs, inventory assets, and review planned file list.
2. Brand assets: recreate stacked/horizontal/mark SVGs and fallbacks; verify transparency/scaling.
3. Tokens/components: centralize light design tokens and reusable form/button/status/evidence primitives.
4. AppShell/routes: add shared navigation and route boundaries while preserving feature clients.
5. Ask/evidence: make the flagship journey readable and evidence-first.
6. Compare: improve controls, matrix, states, and responsive behavior.
7. Reports/News/Sources/Account/Admin: move workflows into owned pages with useful empty/error states.
8. Responsive/accessibility polish and final visual second pass.
9. Run convergence, update README/ADR/design docs/status, and commit each vertical slice.

## Complexity Tracking

No constitution violations. A new component layer is justified only for shared presentation and
token reuse; domain/API duplication is explicitly rejected.
