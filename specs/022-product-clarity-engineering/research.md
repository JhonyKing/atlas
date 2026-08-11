# Research: Product Clarity and Engineering Portfolio

## Decision 1: One public promise, three actions

**Decision**: Keep “Answers you can verify” as the primary promise and present Ask, Compare, and Reports as three plain-language actions, with Ask as the primary in-page workflow.

**Rationale**: The baseline screenshot shows two stacked introductions and makes internal orchestration more prominent than the user benefit.

**Alternatives considered**: A marketing-only landing page was rejected because it would hide the working product. Keeping the live agent catalog above the form was rejected because it requires infrastructure knowledge before task selection.

## Decision 2: Automatic sources with progressive disclosure

**Decision**: Omit `product` from the request by default so the existing backend selects across supported collections; retain the existing explicit collection values under a native collapsed advanced control.

**Rationale**: This reuses the current contract and changes only the default presentation. It preserves expert control without requiring the term “corpus” in the primary journey.

**Alternatives considered**: Removing manual selection was rejected because it would remove capability. Guessing a collection in the browser was rejected because server retrieval already owns evidence selection.

## Decision 3: Honest API availability, not a fake origin

**Decision**: Represent missing hosted API configuration as a typed client availability state. Disable or safely reject live actions with localized user copy; never substitute localhost or a fabricated public URL in production.

**Rationale**: The frontend cannot create a real backend by changing a URL. A polished unavailable state fixes the product defect while Feature 018 remains responsible for a real managed API origin.

**Alternatives considered**: Falling back to localhost in production and using an unrelated Vercel URL were rejected as misleading and nonfunctional.

## Decision 4: Canonical production domain

**Decision**: Use `https://atlasai-lilac.vercel.app` as metadata base and canonical origin.

**Rationale**: Live inspection returned 200 with no `x-robots-tag` and no Vercel authentication. The team alias returned 302 with `x-robots-tag: noindex`, which is Vercel alias behavior rather than an application robots defect.

**Alternatives considered**: Treating every Vercel alias as canonical was rejected because it creates duplicate search targets and conflicts with the observed redirect policy.

## Decision 5: Evidence-linked engineering page

**Decision**: Explain the system in plain language, then link capabilities to existing public GitHub architecture, ADR, verification, and portfolio artifacts.

**Rationale**: Recruiters need technical depth, but claims must remain inspectable and must not imply that external or production evidence exists when it is still pending.

**Alternatives considered**: Embedding raw internal diagrams and task lists on Home was rejected as too dense. A generic skills list without evidence was rejected as weak portfolio proof.
