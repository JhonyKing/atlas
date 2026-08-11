# Feature 022 — product clarity and engineering portfolio verification

**Status**: P0 implemented and verified locally and in canonical production
**Branch**: `codex/022-product-clarity-engineering`  
**Started**: 2026-08-11

## Baseline audit

The current Home is functional but introduces ATLAS twice. `AgentWorkspace` first asks the visitor
to understand typed tools, permissions, budgets, and approval rules. The cited-answer experience
then repeats the product introduction and exposes manual corpus selection. This creates a long,
dense first visit and makes infrastructure more prominent than the user outcome.

Baseline captures:

- [Desktop 1440×900](artifacts/022/baseline/home-1440x900.png)
- [Mobile 390×844](artifacts/022/baseline/home-390x844.png)

Observed baseline problems:

1. Two competing introductions appear before the answer workflow.
2. Internal agent terminology is above the fold.
3. The mobile first viewport does not reach the actual question field.
4. “Evidence state” and “corpus” are presented as prerequisites rather than optional detail.
5. Examples are documentation questions rather than realistic AI engineering decisions.
6. A missing hosted API origin can surface the literal configuration key to visitors.
7. The portfolio attribution and engineering explanation do not exist in the public UI.

## Live production and robots audit

Inspection used the public Vercel project and anonymous HTTP responses on 2026-08-11.

| URL | Status | `x-robots-tag` | Vercel authentication | Finding |
|---|---:|---|---|---|
| `https://atlasai-lilac.vercel.app/` | 200 | absent | absent | Canonical production candidate is public and indexable |
| `https://atlasai-jhonykings-projects.vercel.app/` | 302 | `noindex` | absent | Vercel team alias redirects and is intentionally non-canonical |
| `/en`, `/es`, `/compare`, `/reports`, `/news`, `/sources`, `/account` on the canonical domain | 200 | absent | absent | Existing public routes are anonymously reachable |
| `/engineering` on the canonical domain | 404 | absent; 404 HTML includes `meta robots=noindex` | absent | Route does not exist yet; 404 noindex is expected |

Conclusion: production is not globally sending `noindex`. The reported header belongs to the
non-canonical team alias. Feature 022 will declare `atlasai-lilac.vercel.app` as canonical and add
indexable Home and Engineering metadata; it will not attempt to defeat Vercel's preview/alias
indexing policy.

## SpecKit analysis

Cross-artifact analysis covered 18 functional requirements, 8 measurable success criteria, and 38
tasks.

- Requirement/task coverage: 100%
- Critical findings: 0
- High findings: 0
- Constitution conflicts: 0
- Minor remediation: T009 now requires the Engineering route to expose ten evidence-linked
  capabilities or an explicit limitation.

## P0 verification ledger

### Automated checks

All frontend checks used Node.js 24, matching the configured Vercel runtime.

| Check | Result |
|---|---|
| Vitest | 12 files, **44/44 passed** |
| TypeScript | strict typecheck passed |
| ESLint | passed |
| Next.js production build | passed; 15 static pages generated and `/engineering`, `robots.txt`, and `sitemap.xml` present |
| Focused public/product Playwright | **6/6 passed** |
| AppShell/navigation Playwright | **5/5 passed** |
| Desktop/mobile visual QA | **4/4 passed** |
| Seven-width viewport matrix | **56/56 passed** across Home, Engineering, and existing routes |

The component and browser contracts verify the three Home actions, automatic source selection,
closed Advanced options, bilingual Engineering routes, ten evidence-linked capabilities, safe
hosted API-unavailable copy, public route reachability, semantic headings, and mobile overflow.

### Final visual evidence

- [Home — 1440x900](artifacts/022/final/home-1440x900.png)
- [Home — 390x844](artifacts/022/final/home-390x844.png)
- [Engineering — 1440x900](artifacts/022/final/engineering-1440x900.png)
- [Engineering — 390x844](artifacts/022/final/engineering-390x844.png)

The four captures were inspected directly. Home presents one product promise, three actions, and
the question workflow in the initial desktop/mobile experience. Engineering presents the
architecture and evidence cards without horizontal overflow; advanced agent controls remain
closed by default. The header contains one locale control.

### React and accessibility review

- Route pages remain Server Components and own metadata; interactive state stays in client
  feature components.
- Static capability definitions are outside render paths and no async Client Components were
  introduced.
- Progressive disclosure uses native `details`/`summary`; controls retain labels, focus treatment,
  and keyboard behavior.
- The safe API-unavailable state disables an impossible submission and never displays a raw
  environment key or exception message.

### Hosted boundary

Pull request [#2](https://github.com/JhonyKing/atlas/pull/2) merged the feature to protected `main`
as verified commit `6d810fc2d717e2e04f92b68192032a4bedde40c2`. GitHub Actions run
`31496103046` passed backend, web, database, offline-eval, security-regression, and deployment
contract gates; run `31496103033` passed the cited-answer evaluation, and run `31496103065` passed
repository/evidence contracts. The database gate was rerun after its first attempt could not bind
Docker port 55432; the retry passed in 28 seconds without a code change.

Vercel production deployment `dpl_EGRvByCxGhkrsHLmUNFSx7JR1WVr` is READY for that exact commit.
Anonymous HTTP verification against `https://atlasai-lilac.vercel.app` produced:

- **21/21** public route variants returned 200 across unprefixed, `/en`, and `/es` paths;
- **0** Vercel authentication pages and **0** raw `NEXT_PUBLIC_API_ORIGIN` occurrences;
- Home and Engineering in all three route variants exposed title, canonical, OpenGraph, and
  index/follow metadata (**6/6**);
- `x-robots-tag` was absent from canonical production responses;
- `robots.txt` and `sitemap.xml` returned 200, and the sitemap includes Engineering routes.

The PR preview remained protected by Vercel Authentication, which is acceptable for a preview and
does not represent canonical public access. The canonical production deployment is the anonymous
surface verified above.

The complete research runtime is still not claimed live: Feature 018 must provision the managed
API/worker and configure the real `NEXT_PUBLIC_API_ORIGIN`. Feature 022 fixes the public failure
mode; it does not fabricate a backend URL.

P1 and P2 remain open and are not part of the P0 completion claim.
