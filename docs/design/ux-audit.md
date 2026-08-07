# ATLAS UX Audit (Feature 020 baseline)

**Date**: 2026-08-07
**Scope**: `apps/web` only; no backend/API behavior was changed for this audit.

## Executive finding

ATLAS already contains valuable evidence-first features, but the current root page renders most
of them as one vertical stream. The result is technically functional but does not communicate a
primary research journey, route ownership, or the separation between public research, account data,
and internal operations. Feature 020 will fix the product structure first, then apply a coherent
light design system.

## What was inspected

- Next.js App Router routes under `apps/web/src/app`.
- Feature components under `apps/web/src/features` and their existing tests.
- `globals.css`, `layout.tsx`, `next.config.ts`, locale provider, API clients, and Playwright/Vitest configuration.
- Existing evidence, comparison, report, news, corpus, auth, private-data, and human-review components.
- All files under `imgs/` and their dimensions/transparency.

## Current route and component observations

| Area | Current evidence | UX impact | Direction in Feature 020 |
|---|---|---|---|
| Home | `src/app/page.tsx` renders corpus, governance, review, news, auth, private data, cited answer, and reports in one `<main>`. | No clear flagship action; public and operational concerns compete. | Make Ask ATLAS the home journey and move other surfaces to routes. |
| Locales | `/en` and `/es` delegate to the same `HomePage`; locale copy is selected client-side. | URL structure exists, but route/page composition and shell are not explicit. | Keep locale contracts and add route-aware AppShell/navigation. |
| Navigation | No shared AppShell/navbar is present in `layout.tsx`. | Users cannot discover workflows as a product map. | Add shared responsive shell with active route state. |
| Ask | `CitedAnswerForm` already streams progress, answer, claims, citations, feedback, and abstention. | Valuable behavior is buried after unrelated panels and uses legacy global styles. | Preserve API/SSE and redesign hierarchy, form, progress, evidence, and citations. |
| Compare | `/[locale]/compare` exists; checkboxes and matrix are functional. | Controls are native/unstructured; route lacks shared shell and responsive table strategy. | Add chips/fields, evidence-state language, responsive matrix, and inspectable cells. |
| Reports | `ReportRequest` asks for a completed comparison ID on the homepage. | Manual identifier is poor primary UX and the workflow is not discoverable. | Add `/reports` with recent research/comparison entry points; keep manual mode secondary. |
| News | `DailyNews` is rendered on home and has ready/unavailable evidence states. | Editorial signal is mixed with auth/corpus/admin surfaces. | Move to `/news` and give it an editorial hierarchy. |
| Sources | `CorpusStatus` has useful collection counts and freshness; governance is separate but also on home. | Source trust and internal governance are conflated. | `/sources` for public verified corpus; admin governance under `/admin`. |
| Account | `SessionPanel`, private resources, and upload are all home panels; auth copy defaults to Spanish. | Optional login and private data do not have a coherent account journey. | `/account` with styled auth, private resources, ownership/error states. |
| Admin | `GovernancePanel` and `ReviewPanel` are public root panels; `ReviewPanel` contains hard-coded fixture IDs. | Internal controls look public and can imply fake operational behavior. | Move to `/admin/*`; preserve backend contracts and remove fake-ID primary UX. |
| Styling | `globals.css` repeats literal colors, uses a single global form/button style, and has limited responsive rules. | Visual drift, weak hierarchy, and native controls remain. | Centralize tokens and introduce reusable components incrementally. |
| Branding | No web-ready logo assets or manifest icons are present in the inspected web tree. | ATLAS identity is text-only in the shell/page. | Recreate SVG variants from approved transparent references and add usage rules. |

## Strengths to preserve

- Evidence and citation components already carry source metadata, excerpts, capture/publish dates,
  versions, and canonical links.
- Answer and comparison flows expose real progress/terminal states and cancellation behavior.
- Locale catalogs already contain substantial English/Spanish product copy and evidence labels.
- Existing feature tests provide behavior guardrails for answer, evidence, comparison, corpus, news,
  and accessibility-related rendering.
- API clients are isolated per feature and can be reused under route-level pages.

## High-priority usability problems

1. Information architecture: too many unrelated surfaces on one page.
2. No persistent navigation or active route context.
3. Ask ATLAS is not above the fold as the clear primary action.
4. Report creation starts from a raw ID instead of a completed research artifact.
5. Governance and human review are exposed in the public home flow.
6. Evidence states are not yet expressed through a shared component/semantic language.
7. Repeated literal colors/radii/spacing make visual consistency difficult.
8. Native inputs/checkboxes and generic buttons are not yet a product-level form system.
9. Mobile/table behavior is not documented or verified at the required widths.
10. Brand references are raster-only and must be converted into clean web-ready variants.

## Planned files before implementation

The first implementation slices are expected to touch only these areas, subject to task-level review:

- `apps/web/public/brand/` for SVG/PNG/favicon assets.
- `apps/web/src/app/globals.css` or a focused token/style module for design tokens.
- `apps/web/src/app/layout.tsx` and new `apps/web/src/components/layout/` for AppShell/navigation.
- New route pages under `apps/web/src/app/[locale]/` for `/reports`, `/news`, `/sources`, `/account`, `/admin/*`.
- New reusable components under `apps/web/src/components/` and focused feature presentation files.
- Existing feature components only where needed to preserve behavior while improving structure.
- `apps/web/tests/` or existing feature `__tests__` for route, accessibility, and visual smoke checks.
- `playwright.config.ts` and a documented screenshot/evidence output path for visual QA.
- `docs/design/` and `docs/verification/` for decisions and evidence.

No backend files, API schemas, persistence modules, SSE contracts, or provider integrations are in
scope for the UX/UI feature.

## Audit conclusion

Proceed to planning and implementation in vertical slices. Do not begin by rewriting every feature
component. Start with brand asset inventory, tokens, AppShell, and route boundaries; then move the
existing functional journeys into their proper surfaces.
