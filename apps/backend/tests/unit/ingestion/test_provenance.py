from atlas.ingestion.chunker import chunk_markdown
from atlas.ingestion.normalizer import detect_language, normalize_document


def test_normalizer_records_language_and_page_count() -> None:
    document = normalize_document(
        "# The guide\n\nThis is the first page.\f# La guía\n\n¿Qué permite?".encode(),
        content_type="text/markdown",
    )

    assert document.page_count == 2
    assert document.language == "es-MX"
    assert document.ocr_used is False


def test_chunks_carry_page_and_ocr_provenance() -> None:
    markdown = "# Page one\n\nEnglish text.\f# Page two\n\nTexto OCR."
    chunks = chunk_markdown(
        markdown,
        max_chars=80,
        source_language="es-MX",
        ocr_used=True,
        ocr_confidence=0.91,
    )

    assert {chunk.page_start for chunk in chunks} == {1, 2}
    assert all(chunk.language == "es-MX" for chunk in chunks)
    assert all(chunk.ocr_used and chunk.ocr_confidence == 0.91 for chunk in chunks)


def test_language_detector_falls_back_to_unknown() -> None:
    assert detect_language("12345 symbols only") == "unknown"
