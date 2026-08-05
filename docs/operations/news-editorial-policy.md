# ATLAS previous-day news editorial policy

The daily-news card is an evidence surface, not an editorial claim that ATLAS
knows the objectively most important story. The selection is published only
when the UTC previous-day window has enough attributable signals.

## Source and copyright limits

- Feeds remain allowlisted and operator-reviewed before network activation.
- ATLAS stores title, a bounded summary, publisher, canonical URL, publication
  time, capture time and a content hash; it does not store the full article.
- The original title/summary and canonical link remain labelled in both locales.
- Syndicated items are deduplicated by canonical URL and content hash.

## Corrections and takedowns

An operator can disable a feed or mark a candidate unavailable without changing
historical answer evidence. For a correction or takedown, remove the candidate
from the next selection window, record the UTC action and reason, and preserve
only the minimum audit metadata required by the retention policy. Never replace
the item with an older story merely to fill the card.

## Safety and uncertainty

The card shows `unavailable` when the ranking threshold or attribution evidence
is insufficient. Feed instructions are treated as untrusted content and never
as commands. Network failures, redirects outside the allowlist, oversized
responses and unapproved robots/licensing state fail closed.
