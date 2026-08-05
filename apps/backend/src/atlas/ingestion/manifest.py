"""Load and validate the reviewed, versioned real-corpus manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

from atlas.domain import CollectionSlug, SourceType
from atlas.ingestion.connectors import SourceCandidate


class ManifestError(ValueError):
    """The corpus manifest is malformed or violates its URL policy."""


@dataclass(frozen=True, slots=True)
class CorpusManifest:
    version: str
    review_status: str
    candidates: tuple[SourceCandidate, ...]

    @property
    def source_count(self) -> int:
        return len(self.candidates)


def load_manifest(path: Path) -> CorpusManifest:
    """Read a YAML manifest with safe loading and strict source validation."""

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ManifestError("corpus manifest cannot be read") from exc
    if not isinstance(raw, dict):
        raise ManifestError("corpus manifest must be an object")
    version = raw.get("version")
    review_status = raw.get("review_status")
    collections = raw.get("collections")
    if not isinstance(version, str) or not version.strip():
        raise ManifestError("manifest version is required")
    if not isinstance(review_status, str) or not review_status.strip():
        raise ManifestError("manifest review_status is required")
    if not isinstance(collections, dict):
        raise ManifestError("manifest collections are required")

    candidates: list[SourceCandidate] = []
    seen: set[str] = set()
    for raw_collection, raw_data in collections.items():
        try:
            collection = CollectionSlug(raw_collection)
        except ValueError as exc:
            raise ManifestError(f"unsupported collection: {raw_collection}") from exc
        if not isinstance(raw_data, dict):
            raise ManifestError(f"collection {collection} must be an object")
        publisher = raw_data.get("publisher")
        allowed_host = raw_data.get("allowed_host")
        sources = raw_data.get("sources")
        if not isinstance(publisher, str) or not isinstance(allowed_host, str):
            raise ManifestError(f"collection {collection} needs publisher and allowed_host")
        if not isinstance(sources, list) or not sources:
            raise ManifestError(f"collection {collection} needs sources")
        for item in sources:
            if not isinstance(item, dict):
                raise ManifestError(f"source in {collection} must be an object")
            title, url, source_type = item.get("title"), item.get("url"), item.get("type")
            if not all(
                isinstance(value, str) and value.strip()
                for value in (title, url, source_type)
            ):
                raise ManifestError(f"source in {collection} needs title, url and type")
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.username or parsed.password:
                raise ManifestError("manifest sources must be HTTPS URLs without credentials")
            if (parsed.hostname or "").casefold().rstrip(".") != allowed_host.casefold().rstrip(
                "."
            ):
                raise ManifestError("source host does not match the collection allowlist")
            if url in seen:
                raise ManifestError("manifest contains a duplicate URL")
            try:
                normalized_type = SourceType(source_type)
            except ValueError as exc:
                raise ManifestError(f"unsupported source type: {source_type}") from exc
            seen.add(url)
            candidates.append(
                SourceCandidate(
                    collection=collection,
                    canonical_url=url,
                    title=title,
                    source_type=normalized_type,
                )
            )
    return CorpusManifest(
        version=version,
        review_status=review_status,
        candidates=tuple(candidates),
    )


__all__ = ["CorpusManifest", "ManifestError", "load_manifest"]
