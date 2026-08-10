# ADR 0016: Route-owned AppShell and evidence-first visual language

**Status**: Accepted  
**Date**: 2026-08-10

## Context

ATLAS has public research surfaces, optional private-data surfaces, and internal review tools.
They need a shared visual language without making the public product look like an admin console.
The redesign must remain bilingual, preserve inspectable evidence states, and make responsive
quality measurable instead of relying on a single desktop screenshot.

## Decision

1. Keep route composition in a single `AppShell` with explicit locale-aware navigation. Public
   routes and internal `/admin/*` routes share tokens but not product framing.
2. Keep design tokens, typography, spacing, radii, focus treatment, state colors, and responsive
   breakpoints in `apps/web/src/app/globals.css` so visual changes are reviewable in one place.
3. Use source SVG brand assets plus generated transparent PNG fallbacks for contexts that cannot
   render the SVG lockup. The generation script is reproducible and dimensions are tested.
4. Treat loading, empty, unavailable, retry, and error states as first-class UI states. The UI
   never implies that a missing backend or unverified corpus is healthy.
5. Make Playwright visual QA part of the feature contract: target 390x844 and 1440x900, with a
   wider viewport matrix and route-state checks for mobile overflow, focus, labels, touch targets,
   reduced motion, contrast, and asset loading.

## Alternatives considered

- Separate layout implementations per route: rejected because navigation, locale behavior, and
  accessibility fixes would drift.
- A single dashboard-style shell for every route: rejected because public research pages would
  inherit internal-operations density and hierarchy.
- Screenshot-only approval: rejected because it misses hidden overflow, keyboard focus, semantic
  labels, and controlled unavailable states.

## Consequences

The frontend gains predictable route ownership and a smaller visual vocabulary, while visual QA
becomes reproducible. Backend/API availability remains a separate deployment concern; isolated
frontend screenshots deliberately abort `/v1/*` requests and verify the resulting UI state.
Generated screenshots stay local and ignored by Git; the Markdown verification records the run,
scope, and limitations.
