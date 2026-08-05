# Tasks: Real Multi-Document Corpus

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Manifest and safety

- [X] T001 [P] Create the allowlisted official-source manifest in `corpus/manifests/launch-v1.yaml`.
- [X] T002 Add license/robots, URL, redirect, type and size validation in `apps/backend/src/atlas/ingestion/manifest.py`.
- [X] T003 Add manifest validation tests in `apps/backend/tests/unit/ingestion/test_manifest.py`.

## Phase 2: Real snapshot (P1)

- [X] T004 Add bootstrap CLI wiring to discover, fetch, normalize, chunk, embed and promote the manifest.
- [X] T005 Add page/OCR/language provenance to normalized documents and chunks.
- [X] T006 Add duplicate-content and atomic-promotion integration tests against PostgreSQL (`database/tests/002_corpus_ingestion.sql`).
- [X] T007 Add verification command that reports documents, pages, bytes, hashes and chunks per collection.
- [X] T008 Switch production runtime corpus provider to verified snapshot and retain demo fallback only for development.
- [X] T009 Add status UI for source/page/chunk counts and demo-versus-verified state.

## Phase 3: Evaluation harness (P2)

- [X] T010 Create the versioned ~60-case dataset in `evals/datasets/rag-v1.jsonl` with ground-truth chunk IDs.
- [X] T011 Add separate eval environment instructions and HTTP runner in `evals/run_offline.py`.
- [X] T012 Implement Hit@k, MRR, context precision/recall, citation precision and freshness evaluators.
- [ ] T013 Add retrieval ablations for k=4/8/10, hybrid retrieval, reranking and anti-hallucination prompting.
- [ ] T014 Run seven-day refresh validation, publish results and run analyze/converge.

## Requirement coverage

| Requirement | Tasks |
|---|---|
| FR-COR-001 | T001, T002, T003 |
| FR-COR-002 | T005, T007 |
| FR-COR-003 | T001, T007, T014 |
| FR-COR-004 | T006, T008 |
| FR-COR-005 | T008, T009 |
| FR-COR-006 | T010, T011, T012 |
| FR-COR-007 | T012, T013 |
| FR-COR-008 | T002, T004, T005 |
| SC-COR-001 | T007, T014 |
| SC-COR-002 | T005, T007 |
| SC-COR-003 | T006, T008, T014 |
| SC-COR-004 | T010, T011, T012 |
