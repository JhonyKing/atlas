"""Operator verification report for promoted corpus snapshots."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Sequence
from typing import Any

import psycopg

from atlas.config import Settings
from atlas.domain import CollectionSlug

_QUERY = """
    SELECT c.slug, s.id, s.canonical_url, sv.id, sv.page_count, sv.byte_size,
           sv.content_sha256, sv.language, sv.ocr_used, count(ch.id)
    FROM atlas.collections AS c
    JOIN atlas.sources AS s ON s.collection_id = c.id
    JOIN atlas.source_versions AS sv ON sv.id = s.current_version_id
    LEFT JOIN atlas.chunks AS ch ON ch.source_version_id = sv.id
    WHERE (%s::text IS NULL OR c.slug = %s::text)
    GROUP BY c.slug, s.id, s.canonical_url, sv.id, sv.page_count, sv.byte_size,
             sv.content_sha256, sv.language, sv.ocr_used
    ORDER BY c.slug, s.canonical_url
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlas-corpus-verify")
    parser.add_argument("--collection", choices=[slug.value for slug in CollectionSlug])
    return parser


def summarize_rows(rows: Iterable[Sequence[Any]]) -> dict[str, Any]:
    collections: dict[str, dict[str, Any]] = {}
    for row in rows:
        slug = str(row[0])
        collection = collections.setdefault(
            slug,
            {
                "collection": slug,
                "source_count": 0,
                "page_count": 0,
                "byte_count": 0,
                "chunk_count": 0,
                "hashes": [],
                "sources": [],
            },
        )
        collection["source_count"] += 1
        collection["page_count"] += int(row[4])
        collection["byte_count"] += int(row[5])
        collection["chunk_count"] += int(row[9])
        collection["hashes"].append(str(row[6]))
        collection["sources"].append(
            {
                "source_id": str(row[1]),
                "canonical_url": str(row[2]),
                "source_version_id": str(row[3]),
                "page_count": int(row[4]),
                "byte_count": int(row[5]),
                "content_sha256": str(row[6]),
                "language": str(row[7]),
                "ocr_used": bool(row[8]),
                "chunk_count": int(row[9]),
            }
        )
    for collection in collections.values():
        collection["hashes"] = sorted(set(collection["hashes"]))
    return {
        "collection_count": len(collections),
        "collections": [collections[key] for key in sorted(collections)],
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings()
    dsn = settings.database_url.get_secret_value().replace(
        "postgresql+psycopg://", "postgresql://", 1
    )
    with psycopg.connect(dsn) as connection:
        rows = connection.execute(_QUERY, (args.collection, args.collection)).fetchall()
    print(json.dumps(summarize_rows(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
