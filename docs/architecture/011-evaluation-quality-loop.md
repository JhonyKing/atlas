# Architecture — evaluation and quality loop

The quality loop composes existing deterministic cited-answer, report and retrieval evaluators with
`quality_loop.py`. Case results preserve IDs and machine-readable reasons. Judge contracts require a
version, rubric criteria and bias controls. Online signals and promotion gates fail closed when
required values are absent or regress. Safe trace tags pass through the existing redaction boundary.
