# Feature 020 Final Visual Review

**Date**: 2026-08-10  
**Scope**: T037, visual-only review of the public and internal route surfaces

## Review coverage

The production build was opened with Playwright at **1440x900** and **390x844** for the
English and Spanish route families. The route set covers the home, comparator, reports,
news, sources, account, admin, governance, review, and source-management surfaces.

Final result: **60/60 routes rendered successfully** and retained screenshots in
`apps/web/test-results/visual-qa-*.png`.

## Findings and resolutions

| Finding | Resolution | Evidence |
| --- | --- | --- |
| The first pass waited for `networkidle` on private/admin pages even though their API was intentionally unavailable in the isolated frontend preview. | The visual harness now aborts only `/v1/*` calls and uses `domcontentloaded`; this tests the UI's controlled unavailable states without waiting for a backend. | `apps/web/tests/e2e/visual-qa-routes.spec.ts`, 60/60 final run |
| Example-question buttons were below the 40 px touch target threshold on narrow screens. | Added a 44 px minimum height to `.ask-example`. | `apps/web/src/app/globals.css`, 49/49 viewport matrix |
| The hidden private-upload input inherited a full-width rule and caused horizontal overflow on Account. | Added a more-specific hidden-input width rule so the control remains 1 px and clipped. | `apps/web/src/app/globals.css`, Account cases in the viewport matrix |
| Mobile navigation and locale controls needed consistent touch sizing. | Navigation links and the locale switch use a 44 px minimum height. | AppShell CSS and viewport matrix |

No new product features were added during this pass. The review focused on hierarchy,
spacing, responsive behavior, states, contrast, citations/controls, and public-versus-admin
surface separation.
