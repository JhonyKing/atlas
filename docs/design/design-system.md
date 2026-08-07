# ATLAS Design System Baseline

**Feature**: 020 UX/UI and brand redesign
**Priority**: Light theme first; dark theme token compatibility only

## Design principles

1. Evidence before decoration: visual hierarchy makes source status and provenance easy to inspect.
2. Calm technical confidence: deep navy, indigo, teal, cyan, and controlled amber; no cyberpunk glow.
3. One clear action per surface: pages guide a research goal instead of stacking all features.
4. Accessible state: every status has label, icon/shape, text, and sufficient contrast.
5. Space is a feature: use 4/8-based rhythm and subtle borders/surfaces instead of large shadows.

## Tokens

The implementation will define these as CSS custom properties in one token layer. Components must
reference tokens rather than repeat raw hex values.

### Brand

| Token | Value | Use |
|---|---|---|
| `--atlas-navy` | `#081A4A` | Logo, high hierarchy, primary controls |
| `--atlas-indigo` | `#3155D9` | Links, selected/focus, primary identity |
| `--atlas-blue` | `#168BFF` | Highlights/activity |
| `--atlas-cyan` | `#20D9FF` | Active technical details/data accents |
| `--atlas-teal` | `#14B8B8` | Evidence/verification accent |
| `--atlas-amber` | `#F5AF19` | Selected citation/freshness attention only |

### Surfaces and text

| Token | Value |
|---|---|
| `--atlas-bg` | `#F5F8FC` |
| `--atlas-surface` | `#FFFFFF` |
| `--atlas-surface-soft` | `#EEF4FA` |
| `--atlas-surface-elevated` | `#F9FBFD` |
| `--atlas-border` | `#D7E2EF` |
| `--atlas-border-strong` | `#BBCBDD` |
| `--atlas-text` | `#10213E` |
| `--atlas-text-secondary` | `#4F627A` |
| `--atlas-text-muted` | `#718197` |
| `--atlas-text-subtle` | `#91A0B2` |

### Evidence semantics

| State | Foreground | Background | Required accompanying content |
|---|---|---|---|
| Supported/verified | `#138A72` | `#E8F6F2` | Supported label + check/icon + evidence count |
| Partial | `#B77912` | `#FFF5DA` | Partial label + explanation/limitation |
| Unsupported | `#B4515A` | `#FCEDEF` | Unsupported label + no-evidence explanation |
| Information | `#3155D9` | `#EDF1FF` | Informational label/text |

### Shape, rhythm, and type

- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96px.
- Radius: 6px small, 10px medium, 14px large, 18px large panels; pills only for statuses/chips.
- Shadow: subtle elevation only; borders and surfaces carry most depth.
- Display: 48–64px desktop; H1 36–48px; H2 28–32px; H3 20–24px; body 15–17px; metadata 12–13px.
- Font: existing Inter/system sans-serif stack; no arbitrary remote font dependency.
- Line height: generous for research text and long evidence excerpts.
- Focus ring: indigo with a visible offset; never remove the browser focus indicator without an equivalent.

## Component states

Buttons, inputs, selects, textareas, checkboxes, file upload, fields, badges, citations, evidence
cards, and progress nodes must cover default, hover, focus-visible, active, disabled, loading,
error, and success. Loading/error/success must include accessible status text.

## Responsive and motion rules

- Validate at 375, 390, 768, 1024, 1280, 1440, and 1920px widths.
- Prefer one-column readable research content on small screens.
- Use a deliberate scroll/stack strategy for comparison matrices.
- Respect `prefers-reduced-motion`; progress remains understandable without animation.
