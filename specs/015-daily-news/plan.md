# Implementation Plan: Previous-Day Evidence News

**Branch**: `codex/015-daily-news` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

## Summary

Add a bounded feed-ingestion and ranking path separate from technical-document retrieval. Store
metadata and short attributed summaries, select a story only from the closed previous-day UTC window,
and expose a bilingual API/UI card with an explicit unavailable state.

## Technical Context

**Language/Version**: Python 3.13 and TypeScript/Next.js  
**Primary Dependencies**: stdlib XML/RSS parser or reviewed feed parser, FastAPI/OpenAPI, existing
request context and LangSmith/OpenTelemetry adapter  
**Storage**: PostgreSQL news candidates and daily selections; no full article archive  
**Testing**: pytest contract/unit/integration tests; frontend locale tests; fixture feeds  
**Target Platform**: Docker local development and Linux API/worker  
**Project Type**: Backend scheduled job plus public web card  
**Performance Goals**: Daily selection available without slowing cited-answer requests  
**Constraints**: Attribution, rights, robots, SSRF, deduplication, no invented fallback  
**Scale/Scope**: One selected story per UTC day, with auditable candidates

## Constitution Check

- Evidence-first and privacy principles pass through attributed metadata and bounded excerpts.
- The ranking is explainable and safe-fails when evidence is insufficient.
- The feature does not turn the answer graph into an unrestricted live-web agent.

## Project Structure

```text
apps/backend/src/atlas/news/
├── feeds.py
├── ranking.py
├── service.py
└── schemas.py
apps/backend/src/atlas/api/routes/news.py
apps/backend/tests/contract/api/test_news.py
apps/web/src/features/news/DailyNews.tsx
corpus/manifests/news-v1.yaml
docs/operations/daily-news.md
```

