# Research Notes: Feature 007

- The existing `RetrievalService` already enforces bounded `top_k`, snapshot selection and stable
  evidence uniqueness. New policies must compose around that contract rather than replace it.
- `Question` already carries product, version and date constraints; filters should extend this with
  explicit language and source type while preserving the existing fields.
- `Evidence` contains source identity, capture/published dates and language metadata, which is enough
  for deterministic authority/freshness fixtures without adding provider-specific fields.
- Reranking is intentionally optional: a paired baseline/candidate report is required before any
  configuration can enable it.
