# Feature 020 Brand Assets Verification

**Date**: 2026-08-07
**Branch**: `codex/020-ux-ui-brand-redesign`
**Slice**: Brand assets (SVG primary)

## Inventory and outputs

- References: three PNG RGBA files, each 1536×1024 with transparent pixels.
- Implemented: `apps/web/public/brand/atlas-mark.svg`.
- Implemented: `apps/web/public/brand/atlas-logo-stacked.svg`.
- Implemented: `apps/web/public/brand/atlas-logo-horizontal.svg`.
- Implemented: `apps/web/public/brand/favicon.svg`.
- Implemented T010: transparent PNG fallbacks for mark, stacked, horizontal, favicon, and Apple touch icon.
- PNG dimensions: mark `512×512`, stacked `840×1040`, horizontal `1440×440`, favicon `64×64`, Apple touch icon `180×180`.
- Reproducible generator: `apps/web/scripts/generate-brand-fallbacks.mjs`, invoked by `pnpm --filter @atlas/web brand:generate`.

## Contract checks

- SVGs contain `viewBox` and accessible `<title>/<desc>` metadata.
- SVGs use vector paths/polygons/lines/circles and controlled gradients.
- No SVG contains `<image>` or `data:image`.
- Assets have no gray screenshot background, checkerboard, or embedded PNG.
- The amber node is an accent; it is not used as a button-system color.

## Functional evidence

- Brand asset Vitest: **9 test files, 24 tests passed** (including 4 new asset checks).
- TypeScript: passed with Node 24.
- ESLint for the new asset test: passed.
- HTTP asset smoke: mark, stacked, horizontal, and favicon each returned HTTP 200 from the local web server.
- PNG fallback contract tests verify the five generated dimensions.

## Visual evidence

- Desktop screenshot (1440×900): [020-brand-desktop.png](../../apps/web/test-results/020-brand-desktop.png)
- Mobile screenshot (390×844): [020-brand-mobile.png](../../apps/web/test-results/020-brand-mobile.png)

Review result: the stacked mark and wordmark render crisply on a light surface at both target sizes;
no accidental overflow or background rectangle is present. AppShell integration is intentionally
deferred to the next vertical slice.
