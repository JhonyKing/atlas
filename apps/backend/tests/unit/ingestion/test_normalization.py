from atlas.ingestion.normalizer import normalize_document


def test_html_normalization_preserves_headings_tables_and_code() -> None:
    document = normalize_document(
        b"<h1>Title</h1><table><tr><td>A</td><td>B</td></tr></table><pre><code>x=1</code></pre>",
        content_type="text/html",
    )
    assert "# Title" in document.markdown
    assert "A" in document.markdown and "B" in document.markdown
    assert "x=1" in document.markdown
    assert len(document.content_sha256) == 64


def test_markdown_normalization_is_stable() -> None:
    first = normalize_document(
        b"# Heading\r\n\r\n```py\r\nx=1\r\n```", content_type="text/markdown"
    )
    second = normalize_document(b"# Heading\n\n```py\nx=1\n```", content_type="text/markdown")
    assert first.markdown == second.markdown
    assert first.content_sha256 == second.content_sha256
