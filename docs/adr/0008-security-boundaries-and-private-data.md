# ADR 0008: layered security boundaries and explicit review status

## Decision

Validate source destinations and redirects before network calls, keep source instructions inert,
allow only server-selected actions, redact content at telemetry/audit boundaries, and require
tenant ownership for private data. CI blocks deterministic security regressions. External review
status is recorded as an explicit open finding rather than inferred from automated tests.

## Consequence

The system has multiple small, testable controls and a clear operational handoff. Some deployment
controls—secret manager wiring, external review and production abuse tuning—remain outside the local
slice and cannot be claimed complete here.
