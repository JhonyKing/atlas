# Implementation Plan: Expanded Curated Corpus and Ingestion Governance

**Branch**: `005-expanded-curated-corpus` | **Date**: 2026-08-06 | **Spec**: [spec.md](spec.md)

## Summary

Extend the existing ingestion pipeline with a governed catalog, deterministic connector adapters,
immutable source/version metadata, policy and takedown state transitions, bounded retries, and a
coverage snapshot consumed by operators. The implementation remains provider-independent and keeps
the existing five public `CollectionSlug` values stable; the larger governed catalog is a separate
domain vocabulary so comparator behavior cannot change accidentally.

## Technical Context

**Language/Version**: Python 3.13, TypeScript/Node 24

**Primary Dependencies**: FastAPI/Pydantic, PostgreSQL/Alembic, httpx, pytest, Playwright,
existing SafeFetcher and NormalizedDocument seams, optional pypdf for textual PDF extraction

**Storage**: PostgreSQL governance tables plus existing corpus source/version tables; deterministic
in-memory repository for unit and contract tests

**Testing**: pytest unit/contract/integration/security suites, SQL migration contracts, deterministic
connector fixtures, Playwright operator coverage journey, ruff, mypy, TypeScript checks

**Target Platform**: local Docker PostgreSQL and existing FastAPI/Next.js application

**Project Type**: modular web application with API, ingestion worker, operator routes, and web panels

**Performance Goals**: allowlist validation before every network request; connector run decisions are
bounded; 99% of scheduled fixture refreshes finish or enter visible retry/dead-letter state within
the configured 6–24 hour schedule; coverage response under 500ms for local catalog size

**Constraints**: no arbitrary browsing; only approved HTTPS destinations; no SSRF/private addresses;
no source body in logs/traces; immutable versions; last-good preservation; private tenant isolation;
no change to the existing public comparator enum or anonymous answer behavior

**Scale/Scope**: 16 deterministic initial collection definitions (10 frameworks and 6 model
providers), extensible connector registry, one operator coverage view, and one private-content seam

## Constitution Check

- Evidence Over Fluency: PASS — every captured version has provenance, hash, policy state, and fixture evidence.
- Spec Before Code: PASS — this plan follows the approved Feature 005 spec and PRD ING-001–ING-015.
- Test and Evaluate First: PASS — connector, policy, normalization, retry, SQL, and browser tests precede implementation tasks.
- Explicit Contracts and Type Safety: PASS — typed governance entities, Pydantic API response, SQL constraints, strict TypeScript.
- Provider Independence: PASS — connectors expose normalized domain records; provider payloads do not escape adapters.
- Security and Privacy by Design: PASS — allowlist/SSRF gates, legal review, tenant checks, redaction, and atomic disablement.
- Observable and Cost-Aware: PASS — run IDs, retry counts, latency, safe error codes, and coverage metrics are recorded.
- Small Vertical Slices: PASS — US1 catalog/discovery is the MVP, then refresh, private content, and governance.
- English-Canonical Engineering: PASS — code/contracts/docs are English; UI can localize labels without changing source identity.

## Research Summary

1. Keep the existing `SafeFetcher`, `NormalizedDocument`, `IngestionService`, and public collection enum stable.
2. Add a governance catalog rather than silently expanding comparator collections.
3. Treat connector payloads as untrusted; parse only bounded fields into typed candidates.
4. Store immutable source versions and promote only clean, policy-approved versions.
5. Preserve last-good versions on failure and make disable/takedown transitions atomic.

## Data Model and Contracts

- [data-model.md](data-model.md) defines collection, source, version, run, policy, and coverage entities.
- [contracts/governance-api.yaml](contracts/governance-api.yaml) defines the operator catalog/coverage boundary.
- [quickstart.md](quickstart.md) defines deterministic refresh, SQL, and browser evidence.

## Project Structure

```text
apps/backend/src/atlas/ingestion/
├── governance.py                 # catalog, policies, versions, retries, coverage
├── connectors/
│   ├── __init__.py                # existing allowlist connector seam
│   ├── github_releases.py         # bounded release/changelog adapter
│   ├── scholarly.py               # OpenAlex/Semantic Scholar adapter
│   └── pricing_snapshots.py       # effective-dated pricing/model snapshots
├── normalizer.py                  # HTML/Markdown/PDF structure preservation
└── fetcher.py                     # existing SSRF-safe bounded fetch
apps/backend/src/atlas/api/routes/governance.py
apps/backend/tests/contract/ingestion/
apps/backend/tests/integration/ingestion/
apps/backend/tests/security/test_ingestion_governance.py
apps/web/src/features/corpus/GovernancePanel.tsx
database/migrations/versions/0022_ingestion_governance.py
database/tests/013_ingestion_governance.sql
docs/architecture/005-ingestion-governance.md
docs/adr/0004-curated-corpus-governance.md
docs/verification/005-expanded-curated-corpus.md
```

## Implementation Sequence

1. Write failing catalog, policy, connector, normalization, and API contract tests.
2. Implement the typed governance repository and 16-source deterministic catalog (US1 MVP).
3. Add release, scholarly, pricing, and bounded discovery adapters; extend normalization for PDF structure.
4. Add version/change detection, retries/dead letters, private connector ownership, policy/takedown, and coverage metrics.
5. Apply the migration and SQL contracts, wire the operator route/panel, run full regression, update docs/ADR/evidence.
6. Run SpecKit analyze and converge; only then mark every task complete and commit the feature.

## Complexity Tracking

| Decision | Simpler alternative rejected | Reason and review condition |
|---|---|---|
| Separate governed catalog vocabulary | Add every provider/framework to public `CollectionSlug` | Would change comparator validation and existing corpus status behavior; revisit after a measured need for comparison across the new catalog. |
| Immutable version records | Update one source row in place | In-place updates destroy reproducibility and conflict with evidence capture dates/hashes. |
| In-memory deterministic repository plus SQL contract | Require Docker for every unit test | Fast local tests remain reproducible while SQL contracts still validate the persistence boundary. |
