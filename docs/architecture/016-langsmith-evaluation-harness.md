# Feature 016 architecture

The harness has three layers: deterministic code graders, optional model/human structured graders,
and a pure promotion gate. The gate is consumed by CI and fails closed when a metric is missing or
regressed. LangSmith receives dataset/experiment/commit/corpus metadata only when explicitly opted
into network execution; hidden inputs and outputs are the default.
