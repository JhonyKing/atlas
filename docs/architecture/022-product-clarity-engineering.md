# Feature 022: product clarity and engineering portfolio architecture

## Presentation boundary

Feature 022 separates two audiences without forking the application or removing capabilities.
`ProductHome` is the default product entry point for ordinary AI users. `EngineeringPage` is the
public technical case study for recruiters and engineers. Both run inside the existing route-owned
`AppShell`, share localization and design tokens, and link to the same real workflows.

## Home composition

The Home flow is:

```text
Outcome promise
  -> Ask / Compare / Create report
  -> trust benefits
  -> question form
  -> verified answer, citations, or truthful unavailable/abstention state
```

The question form sends no collection filter by default, allowing the backend to choose relevant
approved sources. A visitor may open Advanced options and select a collection manually. Internal
agent concepts are not prerequisites for asking a question.

## Engineering composition

`/engineering`, `/en/engineering`, and `/es/engineering` present an architecture flow and ten
evidence-linked capabilities: RAG, agents, retrieval, claim verification, citations, structured
outputs, persistence, evaluations, observability, and architecture. Each claim links to a public
repository artifact. The existing agent workspace remains available inside a closed advanced
disclosure.

## Hosted configuration boundary

`getPublicApiAvailability()` converts missing, invalid, or insecure hosted API configuration into
a typed unavailable state. Public components render localized recovery language and disable the
action; they do not render raw exception messages or environment-variable names. This prevents a
configuration detail from becoming product copy while remaining truthful that the API is offline.

The frontend does not invent a backend URL. Feature 018 owns provisioning the managed API/worker
and setting the real `NEXT_PUBLIC_API_ORIGIN` in Vercel.

## Discovery and access

Root metadata declares the canonical production origin, bilingual description, author, OpenGraph,
Twitter, and index/follow policy. `robots.ts` and `sitemap.ts` publish public discovery routes. The
team alias may still receive Vercel's platform-level `x-robots-tag: noindex`; it is deliberately
non-canonical and does not indicate that the production domain is globally blocked.

## Verification boundary

Unit tests enforce the Home contract and safe environment behavior. Playwright verifies public
routes, three actions, progressive disclosure, Engineering evidence, anonymous reachability, and
desktop/mobile presentation. Final screenshots are versioned under
`docs/verification/artifacts/022/final/`.
