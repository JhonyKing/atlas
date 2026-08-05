# Data Model: Real Multi-Document Corpus

- **Manifest**: version, review status, collection and allowlisted source declarations.
- **Source candidate**: collection, canonical URL, title, type and publisher.
- **Captured source version**: content hash, capture time, page/section provenance, normalized bytes
  and promotion status.
- **Corpus snapshot**: immutable set of active source versions with revision and generated time.
- **Evaluation example**: question, locale, expected status, ground-truth chunk IDs and corpus
  version.

