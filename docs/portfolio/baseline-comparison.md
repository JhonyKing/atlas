# Baseline and post-change comparison

| Slice | Evidence | Result | Limitation |
|---|---|---|---|
| Retrieval quality | Feature 007 JSONL | Hit@5/MRR and freshness recorded | deterministic fixtures |
| Model routing | Feature 008 JSONL | 3/3 router cases passed | live provider cost pending |
| Security | Feature 009 suite | 11 security tests passed | external review pending |
| SLO gate | Feature 010 fixture | fail-closed gate exercised | `measured: false` |
| Quality loop | Feature 011 suite | 17 evaluation tests passed | golden expansion pending |
