# Research: ATLAS UX/UI and Brand Redesign

## Decision 1: Keep existing frontend architecture and move composition before rewriting behavior

- **Decision**: Retain Next.js App Router, feature-local API clients, locale provider, evidence,
  answer, comparison, report, news, auth, private-data, and review behavior. Add route composition,
  shared components, and tokens incrementally.
- **Rationale**: The current product has valuable tested behavior. The brief explicitly forbids
  backend/contract changes and unnecessary rewrites.
- **Alternatives considered**:
  - Rewrite the app from scratch: rejected because it would risk SSE/evidence regressions and lose
    existing tests.
  - Add CSS only: rejected because the main problem is information architecture and route ownership.

## Decision 2: Use the approved PNGs as visual references and recreate SVG assets

- **Decision**: Treat the three transparent RGBA PNGs as stacked, horizontal, and mark references;
  create clean SVG geometry for production and optional transparent PNG fallbacks.
- **Rationale**: SVG scales cleanly, supports responsive usage, and avoids embedding a raster image in
  an SVG. The references contain glow/soft edges that should not become page-wide decoration.
- **Alternatives considered**:
  - Ship the PNGs directly as the primary logo: rejected for scaling/variant/accessibility reasons.
  - Generate a new arbitrary symbol: rejected because the approved mark is canonical.

## Decision 3: Light-first token system

- **Decision**: Add centralized CSS custom properties for the supplied brand/surface/text/evidence
  palette, 4/8 spacing rhythm, radius, subtle shadows, type scale, focus, and motion.
- **Rationale**: Tokens reduce repeated literal values and make later dark-mode preparation possible
  without sacrificing the requested light experience.
- **Alternatives considered**:
  - Add a new styling framework: rejected because the existing CSS architecture is small and can be
    organized without a dependency migration.

## Decision 4: Route-based information architecture

- **Decision**: Make Ask the home journey and create route surfaces for compare, reports, news,
  sources, account, and admin subareas. Move existing panels without changing backend contracts.
- **Rationale**: Users need task-oriented navigation and separation of public research, private data,
  and operations.
- **Alternatives considered**:
  - Keep every feature on the home page: rejected because it is the primary audit finding.

## Decision 5: Playwright visual QA as an implementation gate

- **Decision**: Capture 1440×900 and 390×844 after each vertical slice and check all requested widths,
  route reachability, overflow, focus, semantic labels, contrast, reduced motion, and SVG rendering.
- **Rationale**: Build/tests cannot prove visual hierarchy or responsive quality.
- **Alternatives considered**:
  - Review only one final screenshot: rejected because regressions become difficult to localize.
