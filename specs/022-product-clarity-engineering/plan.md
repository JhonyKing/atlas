# Implementation Plan: Product Clarity and Engineering Portfolio

**Branch**: `codex/022-product-clarity-engineering` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/022-product-clarity-engineering/spec.md`

## Summary

Separate ATLAS into a simple public research experience and an inspectable engineering portfolio. Recompose Home around a concise value proposition, three human-readable actions, an answer form with automatic source selection, and progressive disclosure. Add a factual engineering route, public-safe hosted configuration handling, canonical metadata, and anonymous visual verification without changing backend contracts.

## Priority Plan

| Priority | Outcome | Included in this implementation pass |
|---|---|---:|
| P0 | Home clarity, three actions, automatic sources, advanced options, portfolio attribution, `/engineering`, safe API state, SEO/canonical/robots, anonymous desktop/mobile proof | Yes |
| P1 | Plain-language and hierarchy refinement across the remaining public workflows | No — retained as open tasks |
| P2 | Expanded case study, metrics narrative, richer architecture and usability-informed polish | No — retained as open tasks |

## Technical Context

**Language/Version**: TypeScript 5.9, React 19, Next.js 16 App Router

**Primary Dependencies**: Next.js, React, existing ATLAS locale provider and feature clients

**Storage**: N/A; no persistence change

**Testing**: Vitest, Testing Library, Playwright, Next.js production build

**Target Platform**: Public Vercel web application; Chromium desktop and mobile viewports

**Project Type**: Monorepo web frontend backed by an independently deployed API

**Performance Goals**: Keep the static first viewport immediately readable; do not add a blocking client request to render the product introduction

**Constraints**: Preserve API/SSE and route contracts; no fabricated API origin; no public leakage of configuration identifiers; bilingual parity; anonymous access

**Scale/Scope**: Home, engineering route, shared shell, metadata/robots, public route verification; P1/P2 remain follow-up slices

## Constitution Check

- **Evidence Over Fluency**: Pass. Engineering claims link to existing evidence and limitations; answer verification behavior is unchanged.
- **Spec Before Code**: Pass. Feature 022 spec, plan, contracts, and tasks precede implementation.
- **Test and Evaluate First**: Pass by plan. Copy/behavior, metadata, route, and viewport tests are written before implementation.
- **Explicit Contracts and Type Safety**: Pass. Existing typed API contracts remain unchanged; the presentation contract is versioned below.
- **Provider Independence**: Pass. No model/provider routing change.
- **Security and Privacy**: Pass. Internal configuration names are removed from public errors; no secret or private-data behavior changes.
- **Observable and Cost-Aware**: Pass. No request path is added; availability remains honest when API configuration is absent.
- **Small Vertical Slices**: Pass. P0 is independently deployable; P1/P2 stay open.
- **English-Canonical Engineering**: Pass. Engineering artifacts and code remain English; public UI stays bilingual.

Post-design re-check: all gates pass without exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/022-product-clarity-engineering/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── public-experience.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code

```text
apps/web/
├── src/app/
│   ├── [locale]/engineering/page.tsx
│   ├── engineering/page.tsx
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx
│   └── robots.ts
├── src/components/layout/AppShell.tsx
├── src/features/cited-answer/CitedAnswerForm.tsx
├── src/features/home/ProductHome.tsx
├── src/features/engineering/EngineeringPage.tsx
├── src/i18n/index.ts
├── src/lib/env.ts
└── tests/e2e/
```

**Structure Decision**: Reuse the existing Next.js application, shell, feature clients, and locale provider. Add two presentation-focused feature components and route wrappers; do not move backend or persistence code.

## Baseline Audit

| Finding | Evidence | P0 response |
|---|---|---|
| Home renders `AgentWorkspace` and `CitedAnswerForm` as competing product introductions | `apps/web/src/app/page.tsx`; baseline screenshots | Replace the workspace introduction with three plain-language action links and one primary question flow |
| Internal terms are above the fold | `apps/web/src/features/agent/AgentWorkspace.tsx` | Keep operational tooling available elsewhere; remove it from default Home |
| Manual corpus selection is always visible | `CitedAnswerForm.tsx` | Default to automatic sources and move manual selection into a collapsed advanced control |
| Evidence benefit is repeated using infrastructure language | Home baseline | Consolidate into one user-benefit explanation |
| Examples are documentation-oriented | locale catalog | Replace with realistic decisions and comparisons |
| Raw hosted configuration error is visible | `src/lib/env.ts` plus production screenshot | Convert configuration failure to a typed availability condition and localized product message |
| Metadata only supplies a generic title/description | `src/app/layout.tsx` | Add canonical, OpenGraph, robots, and route-specific engineering metadata |
| Team alias sends `x-robots-tag: noindex`; canonical domain does not | Live Vercel response audit on 2026-08-11 | Declare and link the canonical `atlasai-lilac.vercel.app`; do not attempt to override Vercel alias policy |
| `/engineering` does not exist | Live route returns 404 | Add localized and unprefixed public routes |
| Existing public routes are anonymous | Live audit: 200 without Vercel auth | Preserve and automate this verification |

## Complexity Tracking

No constitution violations or new architectural abstractions are required.
