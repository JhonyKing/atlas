# Data Model: Technology Comparator

## ComparisonRequest

| Field | Type | Rules |
|---|---|---|
| technologies | ordered list of technology IDs | 2–4 distinct supported values |
| criteria | ordered list of criterion IDs | At least one; values from the eight supported criteria |
| product/version/date/language/source_type filters | optional constraints | Applied independently to every technology branch |
| locale | `en-US` or `es-MX` | Presentation only; never changes result identity |
| idempotency_key | bounded string | Required for repeat-safe requests |

## ComparisonRun

| Field | Type | Rules |
|---|---|---|
| id | UUID | Stable public run identifier |
| request_id | UUID | Correlates API, workflow and observability stages |
| visitor_key_hash | opaque string | HMAC-derived; never the raw cookie |
| snapshot_id | UUID | Immutable verified corpus snapshot used by all branches |
| status | enum | `accepted`, `retrieving`, `normalizing`, `verifying`, `completed`, `abstained`, `cancelled`, `failed` |
| created_at/completed_at | UTC timestamps | Required for lifecycle and retention |
| retained_until | UTC timestamp | 30-day anonymous content retention |

## ComparisonMatrix

| Field | Type | Rules |
|---|---|---|
| run_id | UUID | References one ComparisonRun |
| technology_ids | ordered list | Stable order chosen by visitor |
| criterion_ids | ordered list | Stable order chosen by visitor |
| locale-independent result hash | string | Detects accidental claim/value drift between locales |
| summary | optional bounded text | May only summarize verified cells |

## ComparisonCell

| Field | Type | Rules |
|---|---|---|
| technology_id | technology ID | One row dimension |
| criterion_id | criterion ID | One column dimension |
| state | enum | `supported`, `unsupported`, `not_applicable`, `partial`, `contradictory` |
| value | nullable structured value | Required only when state is supported or partial |
| unit | nullable string | Cannot be inferred when source units conflict |
| period/version/date | nullable structured context | Preserves temporal and measurement conditions |
| explanation | bounded text | Required for unsupported, not-applicable, partial and contradictory states |
| evidence_ids | list of UUIDs | At least one for supported/partial/contradictory cells; empty for unsupported/not-applicable |
| evidence | bounded metadata list | Title, publisher, URL, excerpt, capture date, source type and version for each cited ID |

Price cells use `source_type=pricing` only. A framework without a comparable API/model price is
`not_applicable`; a provider with no reviewed pricing evidence is `unsupported`.

## Criterion IDs

`capability`, `tool_calling`, `context`, `latency`, `price`, `license`, `freshness`,
`operational_risk`.

## State transitions

`accepted → retrieving → normalizing → verifying → completed` or `abstained`.
Cancellation may occur before a terminal state and becomes `cancelled`. Provider or persistence
failures become `failed` without publishing an unverified matrix.

## Relationships

- One ComparisonRun has one ComparisonMatrix.
- One ComparisonMatrix has `technology_count × criterion_count` ComparisonCells.
- One ComparisonCell references zero or more immutable evidence records.
- One ComparisonRun consumes one comparison-quota reservation and one corpus snapshot.
