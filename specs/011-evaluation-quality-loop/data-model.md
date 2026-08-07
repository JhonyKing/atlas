# Data Model

- `EvaluationManifest`: dataset/version/category counts/commit.
- `QualityResult`: case ID, metrics, reasons, evaluator version and pass state.
- `DifficultCase`: minimized feedback, owner, labels, source run and review status.
- `QualityGate`: thresholds, observed values, decision and failure reasons.
- `TraceTags`: safe version identifiers for node/tool/model/prompt/retrieval/index/corpus/locale.
