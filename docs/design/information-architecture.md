# ATLAS Information Architecture

**Features**: 020 UX/UI and brand redesign; 022 product clarity and engineering portfolio
**Status**: Implemented baseline with Feature 022 public-product refinement

## Product map

```text
ATLAS
├── Ask ATLAS (/)
│   ├── Answers you can verify
│   ├── Ask, Compare, and Create report entry actions
│   ├── Question with automatic source selection
│   ├── Advanced manual source selector
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
├── Engineering (/engineering)
│   ├── Architecture flow
│   ├── Ten evidence-linked engineering capabilities
│   └── Advanced agent workspace and controls
└── Administration (/admin)
    ├── Sources governance (/admin/sources)
    ├── Human review (/admin/reviews)
    └── Internal governance (/admin/governance)
```

## Navigation rules

- The public primary navigation contains Ask, Compare, Reports, News, Sources, Account, and
  Engineering.
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
| `/engineering` and locale equivalent | Inspect ATLAS as an AI engineering case study | Yes | `EngineeringPage`, `AgentWorkspace` in advanced disclosure |
| `/admin/sources` | Govern corpus sources | Operator | `GovernancePanel` |
| `/admin/reviews` | Review consequential outputs | Operator/reviewer | `ReviewPanel` |
| `/admin/governance` | Internal operational controls | Operator | Existing governance contracts |

## Migration approach

1. Add the shared AppShell and route pages without changing feature API clients.
2. Move one existing panel/workflow per vertical slice and retain links for compatibility where
   needed.
3. Remove public-home rendering of admin/private panels only after their route smoke tests pass.
4. Keep old endpoints and domain behavior unchanged; route/page composition is the migration seam.

## Feature 022 progressive-disclosure rule

Home owns the ten-second explanation and the simplest path to a verified answer. It does not ask a
first-time visitor to understand typed tools, budgets, approval rules, corpus, or evidence-state
terminology. Those concepts remain implemented and inspectable in the Advanced options disclosure
or on `/engineering`. This is a presentation boundary, not a reduction in system capability.
