# Research Notes

- Keep routing decisions as typed data so LangGraph nodes remain provider-independent.
- Treat `gpt-5.6-luna` as the configured primary identifier requested by the product owner; the
  adapter must still reject it if production credentials/capability metadata do not allow it.
- Retry only idempotent provider calls and never retry validation, quota, or policy failures.
- Store price tables as effective-dated records and include the selected record ID in telemetry.
