# Implementation Plan: LangSmith Evaluation Harness

## Architecture

Keep deterministic graders in `evals/evaluators`, structured judge contracts in a provider-neutral
module, and promotion decisions in a pure function consumed by CI. LangSmith remains opt-in and
receives only version metadata by default. Offline artifacts are committed under `evals/results`.

## Quality gates

Tests run before implementation, then the unit suite, offline harness, and a fail-closed promotion
command. External judge and human annotation remain operational evidence, not fabricated local proof.
