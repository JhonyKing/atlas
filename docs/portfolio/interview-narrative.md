# Interview narrative

## Problem

Technical answers from general chat models are fluent but difficult to verify. ATLAS makes evidence,
citations, abstention and provenance first-class.

## Agentic decisions

- The graph classifies intent and depth before choosing answer, comparison, report or abstention.
- Retrieval remains provider-independent and preserves source/version metadata.
- A human-review gate blocks publication when evidence or policy checks fail.

## Failures corrected

The project explicitly fixed an omnibus-branch workflow, incomplete bilingual requirements, weak
retrieval evidence, accidental provider assumptions, missing SLO gates and untracked security gaps.
Each correction is represented by a feature branch, tests, commit and verification artifact.

## Cost and reliability

GPT-5.6 Luna is the configured default. Pricing, budgets, cache invalidation, retries, circuit
breakers and promotion gates are measured policies rather than hidden prompt behavior.
