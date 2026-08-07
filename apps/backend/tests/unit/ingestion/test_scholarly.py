from atlas.ingestion.connectors.scholarly import parse_scholarly_records


def test_scholarly_adapter_normalizes_openalex_and_semantic_scholar_ids() -> None:
    records = parse_scholarly_records(
        {
            "results": [
                {
                    "id": "https://openalex.org/W123",
                    "title": "Reliable Agents",
                    "doi": "https://doi.org/10.1234/example",
                    "publication_date": "2026-07-01",
                }
            ]
        },
        collection="research-papers",
    )
    assert records[0].external_id == "W123"
    assert records[0].canonical_url == "https://doi.org/10.1234/example"
