# Feature 020 Public Research Surfaces

**Date**: 2026-08-10  
**Slice**: Reports, Internet Signal, and corpus sources (T029–T031)

## Delivered

- Reports now use a guided two-step surface, with an explicit manual comparison-ID mode,
  helper/error text, loading progress, artifact state, DOCX/PDF download actions, and deletion feedback.
- News presents the previous-day Internet Signal as an editorial surface with date, attribution,
  signal score, corroboration count, canonical source action, and reason-specific unavailable states.
- Sources present collection status, publisher/source types, source/page/chunk counts, freshness,
  stale/refreshing/unavailable explanations, and canonical-root links.

The UI does not invent recent runs or news. When the API has no result, it shows a bounded empty or
unavailable state and explains what is missing.

## Verification

- Frontend unit tests: **35 passed**.
- TypeScript: **passed**.
- ESLint: **passed**.
- Production build: **passed**, 12 routes generated.
- Playwright route smoke: **18 passed** for `/reports`, `/news`, and `/sources` in English and Spanish
  at 1440×900 and 390×844.
- Screenshots are retained under `apps/web/test-results/visual-qa-*`.

The route smoke validates presentation and reachability; it does not claim a populated production
corpus or a configured managed API origin.
