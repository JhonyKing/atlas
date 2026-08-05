from uuid import UUID

from atlas.ingestion.verify import summarize_rows


def test_verification_report_aggregates_pages_bytes_hashes_and_chunks() -> None:
    rows = [
        (
            "langgraph",
            UUID("00000000-0000-0000-0000-000000000001"),
            "https://docs.example.test/a",
            UUID("00000000-0000-0000-0000-000000000011"),
            3,
            1200,
            "a" * 64,
            "en-US",
            False,
            4,
        ),
        (
            "langgraph",
            UUID("00000000-0000-0000-0000-000000000002"),
            "https://docs.example.test/b",
            UUID("00000000-0000-0000-0000-000000000022"),
            2,
            800,
            "b" * 64,
            "es-MX",
            True,
            5,
        ),
    ]

    report = summarize_rows(rows)

    assert report["collection_count"] == 1
    collection = report["collections"][0]
    assert collection["source_count"] == 2
    assert collection["page_count"] == 5
    assert collection["byte_count"] == 2000
    assert collection["chunk_count"] == 9
    assert collection["hashes"] == ["a" * 64, "b" * 64]
