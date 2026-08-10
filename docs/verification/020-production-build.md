# Feature 020 Production Build Verification

**Date**: 2026-08-10  
**Scope**: T038, production build and responsive smoke evidence

## Build

`pnpm build` completed successfully with Next.js 16.2.12, TypeScript, static page generation,
and the expected 12 application routes. The build produced no route errors.

## Responsive production smoke

- Viewport matrix: **49/49 passed** across 375, 390, 768, 1024, 1280, 1440, and 1920 px.
- Target viewport evidence: **390x844** and **1440x900**.
- Bilingual route visual review: **60/60 passed** at 1440x900 and 390x844.
- Screenshot artifacts: `apps/web/test-results/visual-matrix-*.png` and
  `apps/web/test-results/visual-qa-*.png` (local, intentionally ignored by Git).
- Checks included route status, SVG/favicon loading, no horizontal overflow, focus order,
  touch targets, semantic form labels, reduced motion, and basic main-surface contrast.

The checks used the built app with `ATLAS_PROD_SERVER=1`; no development toolbar or backend
availability was counted as product UI.

## Full regression closeout (T043)

- Frontend unit tests: **35/35 passed** across 10 Vitest files using the workspace Node 24 runtime.
- Frontend E2E and visual tests: **149 passed, 4 skipped** out of 153 Playwright tests against
  the production build. The four skips are deployment smoke tests that require a configured
  hosted origin; all local route, workflow, bilingual, responsive, and visual checks passed.
- Backend regression: **379 passed, 4 skipped**, with no backend source or API contract changes.
- TypeScript, ESLint, and Next production build: passed.

The E2E run was executed from `apps/web` with the existing production server and direct
Playwright CLI so the result was not affected by the local pnpm web-server wrapper.
