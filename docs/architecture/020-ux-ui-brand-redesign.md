# Feature 020: UX/UI and brand architecture

## Route ownership

`AppShell` owns the header, locale switch, skip link, navigation, active-route state, and
public-versus-admin framing. Feature components own the content and state of their route:

- `/` — agent workspace and cited-answer form;
- `/compare` — technology/criteria selection and evidence matrix;
- `/reports` — report request lifecycle and artifact links;
- `/news` — previous-day verified-news state;
- `/sources` — corpus collections, counts, freshness, and canonical links;
- `/account` — optional session, private resources, and upload state;
- `/admin/*` — governance, source management, and human review operations.

Localized routes reuse the same feature components with locale-specific copy; they do not fork
the visual system.

## Visual system

`apps/web/src/app/globals.css` contains the shared color, type, spacing, radius, border, focus,
and breakpoint tokens. Components use semantic state classes for supported, partial,
unsupported, unavailable, loading, and error states. Public surfaces use calmer information
density; admin surfaces use utility panels and explicit operational status.

## Brand assets

Source SVGs live in `apps/web/public/brand/`. The deterministic
`apps/web/scripts/generate-brand-fallbacks.mjs` script produces transparent PNG mark/lockup,
favicon, and Apple-touch assets. The root layout registers the favicon and touch icon metadata.

## Quality contract

The route-state suite verifies controlled unavailable/empty/retry states. The viewport matrix
verifies no overflow, reachable skip-link focus, semantic form labels, reduced motion, touch
targets, contrast, route status, and SVG/favicon loading at seven widths. The production visual
route suite captures all bilingual public/admin routes at 390x844 and 1440x900.
