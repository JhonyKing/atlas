# OpenAI official sources

- **Collection:** `openai`
- **Status:** `disabled`
- **Reviewer:** ATLAS maintainers
- **Review date:** 2026-08-04
- **Business/API terms reference:** <https://openai.com/policies/terms-of-use/>
- **Documentation index:** <https://developers.openai.com/llms.txt>
- **API documentation index:** <https://developers.openai.com/api/llms.txt>
- **Robots page:** <https://developers.openai.com/robots.txt> (`User-agent: *`, `Allow: /` verified on review date)
- **Allowed host when approved:** `developers.openai.com`
- **Allowed path when approved:** `/api/`
- **Attribution:** retain publisher `OpenAI`, canonical URL, capture date, and version/release context;
  do not ingest API responses, account content, keys, or private workspace data.
- **Decision:** robots allows the public developer site, but the terms page includes restrictions on
  automatic/programmatic extraction. The relationship between that restriction and this bounded
  documentation-index use requires human/legal confirmation. Keep the connector disabled until that
  confirmation is recorded.
- **Re-review trigger:** terms/robots/policy change, documentation host/path change, model or release
  metadata source change, or any request to crawl beyond `/api/`.
