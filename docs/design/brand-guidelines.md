# ATLAS Brand Guidelines

**Feature**: 020 UX/UI and brand redesign

## Brand meaning

The ATLAS mark is a futuristic angular A with connected data paths and nodes. It suggests
intelligence, navigation, structured information, evidence relationships, and traceability. The
small amber node is a controlled emphasis point: selected evidence, freshness, or attention—not a
general button color.

## Canonical reference inventory

All three references are PNG files, 1536×1024, RGBA with transparent pixels:

| Reference | Visual role | Observation |
|---|---|---|
| `imgs/ChatGPT Image 7 ago 2026, 04_52_01 p.m. (1).png` | Stacked | Mark above ATLAS wordmark; approved primary composition. |
| `imgs/ChatGPT Image 7 ago 2026, 04_52_02 p.m. (2).png` | Horizontal | Mark at left and ATLAS wordmark at right. |
| `imgs/ChatGPT Image 7 ago 2026, 04_52_02 p.m. (3).png` | Mark | Symbol only; suitable for favicon/mobile/avatar. |

The images contain transparent backgrounds but also raster glow/soft edges. They remain visual
references. Production SVGs must recreate the geometry with paths/polygons/lines/circles and must
not embed the PNGs.

## Required web assets

```text
apps/web/public/brand/
  atlas-logo-stacked.svg
  atlas-logo-horizontal.svg
  atlas-mark.svg
  atlas-logo-stacked.png       # optional fallback generated from approved SVG
  atlas-logo-horizontal.png    # optional fallback generated from approved SVG
  atlas-mark.png               # optional fallback generated from approved SVG
  favicon.svg
  favicon.ico                  # if platform build requires it
  apple-touch-icon.png         # if platform build requires it
```

SVG is the primary asset. PNG fallbacks must have transparent backgrounds and no screenshot frame,
checkerboard, gray rectangle, or embedded SVG/PNG workaround.

## Compositions and use

- **Stacked**: landing hero, splash, login/about; never in a 60px navigation bar.
- **Horizontal**: desktop AppShell navbar, header, footer.
- **Mark**: mobile navbar, favicon, avatar, compact/loading spaces.

## Color and backgrounds

- Light UI background: `#F5F8FC`; surfaces: white/soft/elevated variants.
- Brand colors: deep navy, indigo, electric blue, cyan, teal; controlled amber accent.
- The one approved brand gradient is indigo → electric blue → teal at 135deg, used sparingly in
  logo/accent/selected navigation/loading/visualization.
- Do not place the logo in a gray screenshot-like rectangle or on a busy textured background.
- The asset should remain legible on light surfaces and be structurally ready for a future dark variant.

## Clear space and minimum size

- Clear space: at least the diameter of the outer amber/cyan node around the mark or 1/4 of the mark
  height, whichever is larger.
- Stacked minimum digital width: 120px.
- Horizontal minimum digital width: 128px.
- Mark minimum digital size: 20px; recommended favicon source: 32px/48px.
- Do not stretch, skew, recolor arbitrarily, crop nodes, or add drop shadows/glow in CSS.

## Typography and voice

- Use the existing Inter/system sans-serif stack.
- Product voice is precise, calm, evidence-first, and transparent about uncertainty.
- Headings communicate a research task; helper/error text explains what happened and what to do next.

## Incorrect usage

- Do not use the stacked logo in compact navigation.
- Do not make amber the primary action color.
- Do not wrap the logo in a gray/black rectangle to hide transparency.
- Do not add raster glow, photographic shadows, checkerboard, or decorative circuit backgrounds.
- Do not present unsupported/partial states by color alone.
