# Feature 020 Phase 1 Review

**Date**: 2026-08-07
**Branch**: `codex/020-ux-ui-brand-redesign`
**Decision**: Ready for the first implementation slice (brand assets).

## Inputs reviewed

- User design brief in the supplied attachment.
- `docs/design/ux-audit.md`
- `docs/design/information-architecture.md`
- `docs/design/design-system.md`
- `docs/design/brand-guidelines.md`
- `specs/020-ux-ui-brand-redesign/spec.md`, `plan.md`, `tasks.md`
- Three reference PNGs under `imgs/`

## Findings resolved before coding

- The home page currently mixes public research, account/private data, news, governance, review,
  and report controls; route ownership is now documented.
- The existing feature clients and evidence/SSE behavior are reusable; no backend changes are planned.
- The reference set is inventoried: three 1536×1024 RGBA PNGs with meaningful transparency, covering
  stacked, horizontal, and mark compositions.
- The palette, evidence semantics, spacing/type/radius/motion rules, and component state requirements
  are centralized in the design-system document.
- Brand asset rules prohibit embedding PNGs in SVG and prohibit gray screenshot backgrounds/raster glow.
- Visual QA and accessibility evidence are mandatory per slice, including 1440×900 and 390×844 captures.

## Planned first implementation files

1. `apps/web/public/brand/atlas-mark.svg`
2. `apps/web/public/brand/atlas-logo-stacked.svg`
3. `apps/web/public/brand/atlas-logo-horizontal.svg`
4. `apps/web/public/brand/favicon.svg` and transparent fallbacks if required
5. `apps/web/tests/brand-assets.spec.ts`
6. `docs/verification/020-brand-assets.md`

## Scope guard

This approval covers the documented design foundation and the brand-assets slice only. It does not
authorize backend/API/SSE/persistence changes or broad unreviewed page rewrites. Each subsequent
vertical slice must pass its own functional, responsive, accessibility, and visual QA evidence.
