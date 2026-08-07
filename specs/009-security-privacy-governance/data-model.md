# Data Model

- `AuditEvent`: event type, actor hash, tenant scope, resource ID, outcome, timestamp, metadata.
- `RedactedTrace`: run ID, node/model tags, locale, status, latency and safe version metadata.
- `SecurityFinding`: source, severity, owner, status, evidence link and resolution.
- `ConsentRecord`: subject, scope, locale, version, timestamp and withdrawal state.
- `Tombstone`: resource hash, tenant, deleted-at, retention-until and irreversible aggregate flag.
