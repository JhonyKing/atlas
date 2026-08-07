# Feature 020 — Ask ATLAS and evidence slice

Date: 2026-08-07  
Branch: `codex/020-ux-ui-brand-redesign`

## Delivered

- The home route now presents a focused Ask ATLAS journey with the approved promise, subtle stacked
  logo, source/trust explanation, one primary action, and a source selector.
- Three example questions populate the existing technical-question field without invoking the API.
- Existing SSE behavior, cancellation, validation, abstention, feedback, and answer payloads remain
  unchanged.
- Existing SSE stage names (`accepted`, `retrieving`, `composing`, `verifying`, `completed`) drive a
  semantic research-progress list. The UI does not invent backend stages.
- Answer status uses a text/icon evidence badge and citations use the shared citation card with
  publisher, source type, captured/published dates, version, excerpt, canonical URL, and revision link.
- The legacy locale select remains visually hidden for compatibility with the existing locale test;
  the primary visible language control is the AppShell flag button (`🇲🇽 Español` / `🇺🇸 English`).

## Verification

```text
tsc --noEmit                                      PASS
eslint src tests/e2e/app-shell.spec.ts ask.spec.ts PASS
vitest run                                        10 files / 30 tests PASS
Playwright ask.spec.ts --workers=1                2 tests PASS
```

Unit coverage includes invalid text preservation, SSE progress/completion, cancellation, abstention,
partial answers, citation metadata, inference labels, and locale switching. The new browser checks
cover example-question selection, primary Ask action, Spanish rendering, 390px layout, and horizontal
overflow.

## Visual QA

- Desktop 1440×900: [`020-ask-desktop.png`](../../apps/web/test-results/020-ask-desktop.png)
- Mobile 390×844: [`020-ask-mobile.png`](../../apps/web/test-results/020-ask-mobile.png)

The screenshots were reviewed for hierarchy, logo scale, control sizing, whitespace, bilingual copy,
mobile wrapping, and horizontal overflow.
