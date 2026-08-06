# Previous-day news feed review

- **Status:** `approved`
- **Reviewer:** ATLAS project owner
- **Review date:** 2026-08-06
- **Scope:** public RSS/Atom metadata only; bounded title, summary, publisher, dates and canonical URL.
- **Feeds:** The Verge, Ars Technica, TechCrunch and MIT Technology Review as listed in
  `corpus/manifests/news-v1.yaml`.
- **Robots check:** all four publisher hosts returned `robots.txt` with HTTP 200 on 2026-08-06.
- **Safety limits:** HTTPS host allowlist, two redirects, 2 MB maximum feed, eight-second timeout,
  no full article archive, no user-specific data, and explicit `unavailable` fallback.
- **Re-review trigger:** feed URL, publisher policy, robots instructions, licensing basis, topic
  scope or retention behavior changes.
