# Feature 015 — previous-day evidence news

| Check | Result |
|---|---:|
| News unit/contract tests | **10 passed** |
| Full backend regression | **301 passed, 4 skipped** |
| Real isolated execution | **4/4 feeds**, **60 candidates**, UTC previous-day selection recorded |
| Attribution | Canonical URL, publisher, published/captured timestamps and bounded summary |
| Safe failure | `unavailable` for no evidence, failed feeds or insufficient signal |
| Trace policy | `atlas.news.daily` emits safe scalar metadata; content is excluded |

The real execution is isolated and review-gated. It demonstrates the path without claiming permanent
activation of every publisher feed.
