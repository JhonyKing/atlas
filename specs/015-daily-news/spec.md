# Feature Specification: Previous-Day Evidence News

**Feature Branch**: `codex/015-daily-news`
**Created**: 2026-08-05
**Status**: Draft
**Input**: User request to show the most important Internet news from the previous day, constrained by
the PRD evidence-first and bilingual requirements.

## User Scenarios & Testing

### User Story 1 - Read yesterday's verified headline (Priority: P1)

As a visitor, I can see one clearly dated previous-day Internet/technology news item with source,
publication date, short attributed summary and a link to the canonical article.

**Independent Test**: Load a date with valid feed evidence and confirm the displayed item, date,
publisher and URL are all traceable to stored source metadata.

### User Story 2 - Understand uncertainty (Priority: P1)

As a skeptical reader, I can see when ATLAS cannot select a sufficiently supported “top” story and
receive an explicit unavailable state instead of an invented headline.

### User Story 3 - Use Spanish or English (Priority: P2)

As a visitor, I can switch `/en` and `/es`; interface labels are translated while original headline
and excerpts remain clearly labelled when not translated.

## Requirements

- **FR-NEWS-001**: The system MUST define the previous day as a closed UTC calendar window and
  display the date and timezone.
- **FR-NEWS-002**: The system MUST use a versioned allowlist of public sources and retain canonical
  URL, publisher, publication date, capture date and bounded summary.
- **FR-NEWS-003**: The system MUST rank candidate stories using documented, reproducible signals and
  expose the selected story's evidence; it MUST NOT claim objective importance without enough signal.
- **FR-NEWS-004**: The system MUST deduplicate syndicated stories and reject future/undated items.
- **FR-NEWS-005**: The system MUST return `unavailable` when the window has insufficient evidence.
- **FR-NEWS-006**: The API and UI MUST preserve source attribution, dates, URLs and original-language
  labels in both locales.
- **FR-NEWS-007**: Fetching MUST enforce timeout, size, redirect, robots/licensing and SSRF policy.
- **FR-NEWS-008**: News fetch, ranking and display MUST be observable without PII.

## Success Criteria

- **SC-NEWS-001**: 100% of displayed stories have canonical URL, publisher, publication date and
  capture date.
- **SC-NEWS-002**: A story outside the previous-day UTC window is never displayed as that day's item.
- **SC-NEWS-003**: Feed failure or insufficient evidence yields a clear unavailable state in both locales.
- **SC-NEWS-004**: A reviewer can reproduce the selected ranking from stored candidate metadata.

