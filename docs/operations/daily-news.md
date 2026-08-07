# Daily news operations

ATLAS fetches bounded RSS/Atom metadata from the reviewed allowlist in
`corpus/manifests/news-v1.yaml`. It selects only the closed previous-day UTC window. The service
stores no full article body and returns `unavailable` when evidence is insufficient.

## Evidence and observability

The endpoint emits the `atlas.news.daily` trace with request/run correlation, locale, status, UTC
day, candidate count, selection score, reason code and latency. Titles, summaries, article URLs,
cookies, authorization values and secrets are excluded from trace fields. The trace sink is
optional; a missing or unavailable LangSmith configuration does not fail the API.

The isolated real execution is recorded in `evals/results/daily-news-real-execution.json`. It is not
the same as permanent production activation: the manifest remains review-gated until an operator
confirms current robots, license and publisher terms.

## Corrections, takedown and rights

- Remove a feed from the manifest when its publisher requests takedown or its policy changes.
- Invalidate the affected daily selection and return `unavailable` until a reviewed replacement is
  available; never silently substitute an older day.
- Keep only title/summary metadata within the documented bounds and link to the canonical publisher.
- Record the decision, operator, timestamp and manifest version in the change log.
