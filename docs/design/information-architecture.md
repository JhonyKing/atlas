# ATLAS Information Architecture

**Feature**: 020 UX/UI and brand redesign
**Status**: Proposed baseline for implementation

## Product map

```text
ATLAS
├── Ask ATLAS (/)
│   ├── Technical question
│   ├── Verified source selector
│   ├── Research progress
│   └── Answer, claims, citations, feedback, abstention
├── Compare (/compare)
│   ├── Technology selection
│   ├── Criteria selection
│   ├── Evidence-backed matrix
│   └── Completed comparison actions
├── Reports (/reports)
│   ├── Recent completed research/comparisons
│   ├── Generate PDF/DOCX
│   └── Artifact status/download/retention
├── Internet Signal (/news)
│   ├── Previous-day headline
│   ├── Attribution and evidence
│   └── No-evidence/unavailable explanation
├── Verified Sources (/sources)
│   ├── Collection catalog
│   ├── Counts and freshness
│   └── Canonical roots and verification status
├── Account (/account)
│   ├── Optional sign-in
│   ├── Session state/errors
│   └── Private resources/upload/delete
└── Administration (/admin)
    ├── Sources governance (/admin/sources)
    ├── Human review (/admin/reviews)
    └── Internal governance (/admin/governance)
```

## Navigation rules

- The public primary navigation contains Ask, Compare, Reports, News, Sources, and Account.
- Administration is not in the public primary navigation unless the current identity has operator
  access; it is still reachable by a direct authorized route.
- The horizontal logo is used on desktop. The mark is used in compact/mobile navigation.
- Locale switching preserves the current workflow where a matching localized route exists.
- Active state is communicated by text/weight/border/icon, not color alone.
- Every route has a useful title, one primary action, a stable loading state, an empty state, and a
  contextual error/retry state.

## Route ownership

| Route | Primary user goal | Public? | Existing source to reuse |
|---|---|---:|---|
| `/`, `/en`, `/es` | Ask a technical question | Yes | `CitedAnswerForm`, evidence, corpus selector |
| `/compare` and locale equivalent | Compare technologies | Yes | `ComparisonPage`, `ComparisonMatrix` |
| `/reports` | Turn completed research into an artifact | Yes/auth policy applies | `ReportRequest`, report client |
| `/news` | Read previous-day verified signal | Yes | `DailyNews` |
| `/sources` | Inspect verified corpus | Yes | `CorpusStatus` |
| `/account` | Sign in and manage private data | Optional auth | `SessionPanel`, private panels |
| `/admin/sources` | Govern corpus sources | Operator | `GovernancePanel` |
| `/admin/reviews` | Review consequential outputs | Operator/reviewer | `ReviewPanel` |
| `/admin/governance` | Internal operational controls | Operator | Existing governance contracts |

## Migration approach

1. Add the shared AppShell and route pages without changing feature API clients.
2. Move one existing panel/workflow per vertical slice and retain links for compatibility where
   needed.
3. Remove public-home rendering of admin/private panels only after their route smoke tests pass.
4. Keep old endpoints and domain behavior unchanged; route/page composition is the migration seam.
