# Feature 020 Visual Matrix Verification

**Date**: 2026-08-10  
**Slice**: Responsive, accessibility, and visual QA foundations (T035-T036)

## Matrix

Viewports: **375, 390, 768, 1024, 1280, 1440, and 1920 px**. The target evidence sizes are
explicitly 390x844 and 1440x900.

Routes: `/`, `/compare`, `/reports`, `/news`, `/sources`, `/account`, and `/admin`.

The final production-server run passed **49/49** route/viewport cases. It used
`ATLAS_PROD_SERVER=1`, so the checks represent the built Next.js app rather than the
development toolbar.

## Automated gates

- no horizontal overflow;
- first-tab skip-link focus;
- route reachability;
- favicon request and SVG image completion;
- visible control touch targets;
- labels/ARIA for visible form controls;
- reduced-motion animation limit;
- main-surface foreground/background contrast threshold;
- screenshots retained under `apps/web/test-results/visual-matrix-*`.

The run fixed two real findings: example-question buttons now have a 44 px minimum touch
height, and the visually hidden upload input no longer inherits a full-width rule that caused
horizontal overflow on `/account`.
