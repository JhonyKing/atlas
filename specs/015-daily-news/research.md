# Research: Previous-Day Evidence News

## Decisions

- “Previous day” is the closed UTC calendar day immediately before the request's observed date.
- Feed candidates retain only title, bounded summary, attribution, dates, URL and content hash; full
  article bodies are not archived.
- Selection is deterministic and emits `unavailable` when the ranking signal is insufficient.

## Sources

- Public RSS/Atom feeds must be listed in `corpus/manifests/news-v1.yaml` after an operator review.
- The ranking and attribution model is an ATLAS policy decision, not a claim that any source is
  objectively the most important news outlet.

