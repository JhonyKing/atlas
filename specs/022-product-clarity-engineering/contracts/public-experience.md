# Public Experience Contract

## Home first viewport

The rendered Home MUST expose, before any API response:

1. ATLAS identity.
2. “Answers you can verify” in the selected locale.
3. A one-sentence explanation that ATLAS researches AI topics and supports claims with inspectable sources.
4. Three actions: Ask a question, Compare AI technologies, Create a report.
5. The primary question input or an immediately visible path to it.

The default viewport MUST NOT expose these implementation terms:

- typed tools
- budgets
- approval rules
- corpus
- evidence state
- `NEXT_PUBLIC_API_ORIGIN`

## Advanced options

- Closed by default.
- Summary label: “Advanced options” / “Opciones avanzadas”.
- Contains a source preference whose default is automatic.
- Manual choices reuse existing collection slugs.
- Closing the disclosure does not discard a manually selected choice.

## API availability

- A valid hosted API origin enables the existing request behavior.
- A missing or invalid hosted API origin yields a localized product message.
- No configuration key, stack trace, localhost address, or deployment instruction is rendered.
- No request is sent to an invented origin.

## Engineering page

Public routes:

- `/engineering`
- `/en/engineering`
- `/es/engineering`

The page MUST include RAG, agents, retrieval, claim verification, citations, structured outputs, persistence, evaluations, observability, and architecture. Claims link to `https://github.com/JhonyKing/atlas` evidence.

## Metadata and robots

- Canonical origin: `https://atlasai-lilac.vercel.app`.
- Canonical pages are indexable.
- OpenGraph type is `website`.
- Home and engineering have route-specific titles and descriptions.
- Application metadata does not attempt to remove Vercel's `noindex` header from non-canonical team/preview aliases.

## Anonymous route matrix

At minimum, these unprefixed and locale-prefixed public routes return a product page without Vercel authentication:

- Home
- Compare
- Reports
- News
- Sources
- Account
- Engineering
