# Feature 016 — LangSmith evaluation harness

| Check | Result |
|---|---:|
| Structured grader/gate tests | **20 passed** |
| Offline dataset | `rag-v1.jsonl`, **60/60 cases passed** |
| Promotion gate | **passed** with versioned fixture thresholds |
| Online linkage | opt-in only; dry-run does not call LangSmith |
| Promotion policy | fail-closed for citation, faithfulness, abstention, cost and p95 latency |
| Negative-case export | hashes/question IDs only; raw question and answer omitted |

The promotion artifact is explicitly an offline fixture. Live judge and human-annotation results
must be added as separate evidence before claiming production promotion.
