# Tasks: Real Multi-Document Corpus

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Manifest and safety

- [ ] T001 [P] Create the allowlisted official-source manifest in `corpus/manifests/launch-v1.yaml`.
- [ ] T002 Add license/robots, URL, redirect, type and size validation in `apps/backend/src/atlas/ingestion/manifest.py`.
- [ ] T003 Add manifest and SSRF/redirect contract tests in `apps/backend/tests/contract/ingestion/`.

## Phase 2: Real snapshot (P1)

- [ ] T004 Add bootstrap CLI wiring to discover, fetch, normalize, chunk, embed and promote the manifest.
- [ ] T005 Add page/OCR/language provenance to normalized documents and chunks.
- [ ] T006 Add duplicate-content and atomic-promotion integration tests against PostgreSQL.
- [ ] T007 Add verification command that reports documents, pages, bytes, hashes and chunks per collection.
- [ ] T008 Switch production runtime corpus provider to verified snapshot and retain demo fallback only for development.
- [ ] T009 Add status UI for source/page/chunk counts and demo-versus-verified state.

## Phase 3: Evaluation harness (P2)

- [ ] T010 Create the versioned ~60-case dataset in `evals/datasets/rag-v1.jsonl` with ground-truth chunk IDs.
- [ ] T011 Add separate eval environment instructions and HTTP runner in `evals/run_offline.py`.
- [ ] T012 Implement Hit@k, MRR, context precision/recall, citation precision and freshness evaluators.
- [ ] T013 Add retrieval ablations for k=4/8/10, hybrid retrieval, reranking and anti-hallucination prompting.
- [ ] T014 Run seven-day refresh validation, publish results and run analyze/converge.

