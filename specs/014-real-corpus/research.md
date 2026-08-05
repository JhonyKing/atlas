# Research: Real Multi-Document Corpus

## Decisions

- Use official LangChain documentation under `docs.langchain.com/oss/python/` and OpenAI API
  documentation under `developers.openai.com/api/`.
- Treat the 12-document manifest as an ingestion input, not as proof of a loaded snapshot. The
  bootstrap must record bytes, hashes, pages and chunks before promotion.
- Preserve the existing atomic stage/promote pipeline and the demo fallback only for development.

## Sources

- https://docs.langchain.com/oss/python/langgraph/overview
- https://docs.langchain.com/oss/python/langgraph/graph-api
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langchain/overview
- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/guides/embeddings

