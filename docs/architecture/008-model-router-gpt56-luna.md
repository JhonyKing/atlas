# Architecture — model router and cost controls

`atlas.models` contains provider-independent contracts. `ModelRouter` selects the configured
`gpt-5.6-luna` identifier and reasoning effort from typed task signals. `resilience.py` bounds
timeouts, retries and circuit state. Pricing, budgets and cache keys are pure deterministic
policies. `providers/model_adapter.py` is the common port; SDK-specific clients stay outside the
graph and can be replaced by the deterministic local adapter in tests.

The router records model, policy and selection reason without logging prompts, excerpts or keys.
Promotion uses paired quality/latency/cost gates; a failed candidate never silently becomes the
default.
