# Feature 008 — model router, GPT-5.6 Luna, and cost controls

## Current evidence

| Check | Result |
|---|---:|
| Router/resilience/cost/adapter tests | 8 passed |
| Full backend regression | 286 passed, 4 skipped |
| Batch router JSONL evaluation | 3/3 passed |
| `pnpm test:model-router` | passed |
| Ruff and mypy for router package | passed |
| Default model | `gpt-5.6-luna` |
| Provider SDKs in router contracts | none |

The completed slice covers typed routing, signal-driven reasoning effort, bounded retry/circuit
behavior, effective-dated pricing, daily budget, versioned cache keys, redacted cost records,
common adapter port, embedding-profile fallback, paired promotion gates, and a deterministic batch
router evaluator. Production provider latency/cost measurements remain open evidence, not claims of
completion.

Commands:

```powershell
pnpm test:model-router
apps\backend\.venv\Scripts\python.exe -m atlas.evaluation.model_router `
  --dataset evals/cases/008-model-router-gpt56-luna.jsonl `
  --output docs/verification/008-model-router-gpt56-luna-metrics.json
```
