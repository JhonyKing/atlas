# Implementation Plan: Real Multi-Document Corpus

**Branch**: `codex/014-real-corpus` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

## Summary

Use the existing connector/fetcher/normalizer/chunker/embedding/atomic-promotion pipeline with a
versioned official-source manifest, then add bootstrap verification and a separate evaluation
harness. The deterministic demo remains available for development but is clearly labelled and never
counts as a verified snapshot.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: FastAPI, PostgreSQL/pgvector, existing connectors, pypdf/Tesseract where
authorized, OpenAI embeddings, pytest  
**Storage**: PostgreSQL source/version/chunk/snapshot tables; manifest and eval files in repository  
**Testing**: pytest unit/contract/database tests; offline harness; seven-day refresh validation  
**Target Platform**: Docker local development and Linux worker  
**Project Type**: Backend API, ingestion worker and eval CLI  
**Performance Goals**: A normal refresh is resumable and does not block answer requests  
**Constraints**: Allowlist, robots/license, SSRF controls, bounded content, atomic promotion  
**Scale/Scope**: Initial 12+ official documents across three supported collections

## Constitution Check

- Evidence provenance and safe failure pass through immutable staged/promoted versions.
- Privacy and licensing pass through bounded excerpts and source governance metadata.
- Reproducibility passes through manifest, hashes, counts and versioned eval inputs.

## Project Structure

```text
apps/backend/src/atlas/ingestion/
├── connectors/
├── manifest.py
├── bootstrap.py
└── worker.py
apps/backend/tests/contract/ingestion/
apps/backend/tests/integration/database/
corpus/
├── manifests/launch-v1.yaml
└── README.md
evals/
├── datasets/rag-v1.jsonl
└── run_offline.py
docs/operations/corpus-refresh.md
```

