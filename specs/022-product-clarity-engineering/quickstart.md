# Quickstart: Validate Product Clarity P0

## Prerequisites

- Install repository dependencies.
- Run from `apps/web`.
- No API key is required to validate the static product introduction, metadata, or unavailable state.

## Automated checks

```powershell
npm run lint
npm run typecheck
npm test
npm run build
npx playwright test tests/e2e/product-home.spec.ts tests/e2e/public-metadata.spec.ts tests/e2e/public-routes.spec.ts
```

## Desktop acceptance

1. Open `/en` at 1440×900.
2. Confirm the first viewport explains AI research and verifiable sources.
3. Confirm Ask, Compare, and Create a report are visible.
4. Confirm manual source selection is hidden under Advanced options.
5. Confirm the builder attribution and engineering link are present.
6. Capture the full page to the Feature 022 verification artifact directory.

## Mobile acceptance

1. Open `/es` at 390×844.
2. Confirm there is no horizontal overflow.
3. Confirm the value proposition, primary action, and locale control are readable and reachable.
4. Expand Advanced options and verify manual source selection remains usable.
5. Open `/es/engineering` and verify the technical sections and evidence links stack without clipping.

## Hosted acceptance

1. Open `https://atlasai-lilac.vercel.app` without a Vercel session.
2. Verify the canonical response does not send `x-robots-tag: noindex`.
3. Verify Home and `/engineering` contain canonical and OpenGraph metadata.
4. Verify a missing API origin never renders `NEXT_PUBLIC_API_ORIGIN`.
5. Record that `atlasai-jhonykings-projects.vercel.app` is a non-canonical redirect whose Vercel-managed `noindex` is expected.
