from atlas.ingestion.chunker import chunk_markdown


def test_chunker_preserves_heading_path_and_stable_offsets() -> None:
    markdown = (
        "# Introduction\n\nA short overview.\n\n"
        "## Installation\n\nInstall the package with the documented command.\n\n"
        "## Configuration\n\nSet the environment variable before starting the service."
    )

    chunks = chunk_markdown(markdown, max_chars=80)

    assert [chunk.ordinal for chunk in chunks] == list(range(len(chunks)))
    assert chunks[0].heading_path == ("Introduction",)
    assert any(chunk.heading_path == ("Introduction", "Installation") for chunk in chunks)
    assert any(chunk.heading_path == ("Introduction", "Configuration") for chunk in chunks)
    assert all(0 <= chunk.start_offset < chunk.end_offset <= len(markdown) for chunk in chunks)
    assert all(len(chunk.text) <= 80 for chunk in chunks)
    assert all(len(chunk.text_sha256) == 64 for chunk in chunks)
    assert all(chunk.token_count > 0 for chunk in chunks)


def test_chunker_splits_long_sections_on_paragraph_boundaries() -> None:
    markdown = "# Long section\n\n" + "\n\n".join(
        ["Paragraph one with useful facts.", "Paragraph two with more facts.", "Paragraph three."]
    )

    chunks = chunk_markdown(markdown, max_chars=45)

    assert len(chunks) >= 2
    assert all(chunk.heading_path == ("Long section",) for chunk in chunks)
    assert all("\n\n" not in chunk.text or len(chunk.text) <= 45 for chunk in chunks)
