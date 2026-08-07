"""OpenAlex and Semantic Scholar metadata adapter."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScholarlyCandidate:
    collection: str
    external_id: str
    title: str
    canonical_url: str
    published_at: str | None


def parse_scholarly_records(payload: object, *, collection: str) -> list[ScholarlyCandidate]:
    if not isinstance(payload, dict):
        raise ValueError("scholarly payload must be an object")
    values = payload.get("results") or payload.get("data") or []
    if not isinstance(values, list):
        raise ValueError("scholarly results must be a list")
    output: list[ScholarlyCandidate] = []
    for item in values:
        if not isinstance(item, dict):
            continue
        raw_id = item.get("id") or item.get("paperId")
        title = item.get("title")
        if not isinstance(raw_id, str) or not isinstance(title, str):
            continue
        external_id = raw_id.rstrip("/").rsplit("/", 1)[-1]
        doi = item.get("doi") or item.get("url") or raw_id
        canonical_url = doi if isinstance(doi, str) and doi.startswith("https://") else raw_id
        output.append(
            ScholarlyCandidate(
                collection,
                external_id,
                " ".join(title.split()),
                canonical_url,
                item.get("publication_date")
                if isinstance(item.get("publication_date"), str)
                else None,
            )
        )
    return output
