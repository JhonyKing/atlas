# Implementation Plan: Model Router, GPT-5.6 Luna, and Cost Controls

**Branch**: `codex/008-model-router-gpt56-luna` | **Date**: 2026-08-06

## Summary

Add a typed model-routing boundary with Luna as the configured default, provider adapters, bounded
resilience, effective-dated pricing, versioned cache keys, and deterministic promotion evaluations.

## Architecture

1. `apps/backend/src/atlas/models/contracts.py` defines model requests/responses and selection metadata.
2. `router.py` selects approved models from task signals and server settings.
3. `resilience.py` owns timeout/retry/circuit/fallback policy.
4. `pricing.py` and `budget.py` calculate versioned cost and enforce limits.
5. `cache.py` creates tenant-safe evidence-pack keys with version components.
6. `adapters/` hides provider SDKs from graph nodes.
7. `benchmark.py` evaluates paired baseline/candidate results.

The existing answer service continues to accept provider-independent ports. Luna is a configuration
default and telemetry value, not a hard-coded SDK dependency in agent nodes.

## Quality Gates

- tests before implementation;
- no secrets/prompts/excerpts in logs;
- full backend regression plus Ruff/mypy;
- deterministic benchmark output before any default change;
- document README, architecture and ADR at closure.
