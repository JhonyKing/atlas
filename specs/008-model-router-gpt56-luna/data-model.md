# Data Model

- `ModelSelection`: model, provider, reasoning effort, policy version, and selection reason.
- `ProviderAttempt`: attempt number, outcome class, latency, retry delay, and redacted error code.
- `PriceVersion`: provider/model, input/output rates, effective interval, and immutable ID.
- `CostRecord`: token counts, price version, estimated cost, budget bucket, and run ID.
- `CacheKey`: tenant scope plus corpus, retrieval, prompt, model and embedding versions.
- `BenchmarkResult`: dataset, candidate/baseline metrics, latency, cost and promotion decision.
