# Feature 013 — LangSmith quality observability

| Check | Result |
|---|---:|
| Observability unit/contract tests | **8 passed, 1 skipped** (network smoke is opt-in) |
| LangSmith dry-run | **passed**, no network, dataset or model call |
| Offline evaluation harness | **60 cases discovered**; dry-run completed |
| Default trace policy | Inputs/outputs hidden; safe metadata only |
| Unconfigured LangSmith path | No-op sink keeps API available |

The implementation uses an internal trace-sink port, so LangSmith is optional and outages do not
make answer requests fail. The opt-in network smoke test remains operational evidence and must be
run only when the operator intentionally enables `ATLAS_LANGSMITH_SMOKE=1` with valid secrets.

Still pending from the PRD backlog: modern-stack decision record, promotion contract, cost evidence,
complete feedback-to-review queue, A/B promotion evidence and a portfolio capture without PII.
