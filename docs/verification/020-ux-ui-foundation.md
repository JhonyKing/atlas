# Feature 020 — UX/UI foundation and route separation

Date: 2026-08-07  
Branch: `codex/020-ux-ui-brand-redesign`

## Delivered slice

- Reusable `AtlasLogo` variants reference the approved SVG mark, stacked wordmark, and horizontal wordmark.
- Shared form primitives cover buttons, labels, helper/error messaging, inputs, textarea, select,
  checkbox, and file upload with focus, disabled, loading, and danger states.
- Evidence primitives expose a text/icon state for supported, partial, unsupported, and contradictory
  results; citation cards preserve publisher, source type, excerpt, and canonical link metadata.
- Research progress is a semantic ordered list of only the statuses supplied by the caller.
- The homepage is now the Ask/agent journey. Corpus, news, reports, account/private data, governance,
  and human review remain available through their route owners.
- The locale switcher shows `🇲🇽 Español` while English is selected and `🇺🇸 English` while Spanish is
  selected. Its accessible name describes the destination language.
- The LocaleProvider now applies URL/persisted locale after a stable server/client first render,
  removing the `/es` AppShell hydration mismatch.
- AppShell includes a keyboard-visible `Skip to content` link targeting the content frame.

## Verification evidence

Commands were run from `apps/web` with the bundled Node 24 runtime:

```text
tsc --noEmit                                      PASS
eslint src tests/e2e/app-shell.spec.ts            PASS
vitest run                                        10 files / 30 tests PASS
Playwright app-shell.spec.ts --workers=1          4 tests PASS
```

The Playwright suite verified:

1. Public navigation and active Ask state.
2. English/Spanish locale switching and both flag labels.
3. HTTP 200 for `/`, `/compare`, `/reports`, `/news`, `/sources`, `/account`, all admin routes,
   and their `/es` equivalents.
4. No corpus, news, auth, reports, governance, or review panels on the public homepage.
5. Mobile menu discovery at 390px with `aria-expanded` transitions.
6. Keyboard skip-link target and accessible locale target labels.

The route smoke is intentionally HTTP-based for the route loop because the Next development server
compiles the first localized route lazily; the browser interaction tests still exercise the rendered
AppShell and mobile behavior.

## Visual evidence

- Desktop 1440×900: [`020-ux-foundation-desktop.png`](../../apps/web/test-results/020-ux-foundation-desktop.png)
- Mobile 390×844, Spanish: [`020-ux-foundation-mobile-es.png`](../../apps/web/test-results/020-ux-foundation-mobile-es.png)

## Remaining work

This slice does not claim the full redesign is complete. T010 (PNG/icon fallbacks), the Ask visual
workflow, evidence integration into the live answer, and the remaining Compare/Reports/News/Sources/
Account/Admin responsive and visual QA slices remain open in `specs/020-ux-ui-brand-redesign/tasks.md`.
