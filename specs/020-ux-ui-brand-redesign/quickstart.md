# UX/UI Redesign Quickstart

## Phase 0: inspect and review

Read:

- [UX audit](../../docs/design/ux-audit.md)
- [Information architecture](../../docs/design/information-architecture.md)
- [Design system](../../docs/design/design-system.md)
- [Brand guidelines](../../docs/design/brand-guidelines.md)
- [Frontend QA contract](contracts/frontend-qa.md)

Inspect the three reference assets under `imgs/` before changing logo files.

## Local app

```powershell
# API and database
docker compose up -d

# frontend (repository standard)
pnpm --filter @atlas/web dev
```

Open `http://localhost:3000/`, `http://localhost:3000/en`, and
`http://localhost:3000/es`. Verify the API health separately at
`http://localhost:8000/healthz`.

## Functional gates

```powershell
pnpm --filter @atlas/web lint
pnpm --filter @atlas/web typecheck
pnpm --filter @atlas/web test
pnpm --filter @atlas/web test:e2e
```

The test runner must use the repository-supported Node version (Node 24) and the lockfile.

## Visual QA

After every vertical slice, capture 1440×900 and 390×844 screenshots and inspect:

- hierarchy/whitespace/alignment/type;
- logo sizing/SVG transparency;
- evidence status labels/icons/text;
- focus/contrast/touch targets;
- no horizontal overflow;
- truthful loading/empty/error states.

The required route/viewport matrix is documented in `contracts/frontend-qa.md`.
