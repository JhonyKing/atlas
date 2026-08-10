# Feature 020 Comparator Verification

**Date**: 2026-08-10  
**Slice**: Comparator controls and evidence matrix (T026–T028)

## Delivered

- Technology and criterion controls use native checkboxes inside keyboard-focusable chips.
- Each chip exposes a visible `Selected`/`Available` state; adding a fifth technology is disabled.
- The matrix includes a text-and-icon legend for supported, partial, unsupported, and contradictory states.
- Cells retain bounded explanations and evidence IDs inside an expandable inspection panel.
- The table remains readable on narrow screens through a labelled, keyboard-focusable horizontal region.
- The existing POST/SSE comparison contract is unchanged.

## Verification

- Frontend unit tests: **35 passed**.
- TypeScript: **passed**.
- ESLint: **passed**.
- Playwright mocked SSE matrix journey: **1 passed** at 1440×900.
- Playwright existing comparator route checks: **2 passed** at 1440×900 and 390×844.
- Screenshots: [`020-compare-desktop.png`](../../apps/web/test-results/020-compare-desktop.png),
  [`020-compare-mobile.png`](../../apps/web/test-results/020-compare-mobile.png), and
  [`020-compare-matrix-desktop.png`](../../apps/web/test-results/020-compare-matrix-desktop.png).

The mocked SSE journey validates presentation and accessibility without pretending that the
development Supabase corpus is populated. It does not claim live API or production data coverage.
