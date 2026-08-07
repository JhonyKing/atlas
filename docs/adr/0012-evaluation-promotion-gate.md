# ADR 0012: deterministic quality gate before online judges

The evaluation harness runs deterministic checks first and applies a fail-closed gate to citation,
faithfulness, abstention safety, cost and p95 latency. LangSmith judges and human annotations are
optional enrichment; they cannot bypass a failed deterministic threshold. Fixture metrics are
labelled as such and are not production-capacity evidence.
