from pathlib import Path

import pytest

from atlas.ingestion.manifest import ManifestError, load_manifest

MANIFEST = Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "launch-v1.yaml"
EXPANSION_MANIFEST = (
    Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "expansion-v1.yaml"
)


def test_launch_manifest_is_multi_document_and_uses_official_hosts() -> None:
    manifest = load_manifest(MANIFEST)

    assert manifest.version == "launch-v1"
    assert manifest.review_status == "approved"
    assert manifest.source_count == 12
    assert {candidate.collection.value for candidate in manifest.candidates} == {
        "langgraph",
        "langchain",
        "openai",
    }
    assert all(candidate.canonical_url.startswith("https://") for candidate in manifest.candidates)


def test_manifest_rejects_duplicate_urls(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(
        """
version: test
review_status: approved
collections:
  openai:
    publisher: OpenAI
    allowed_host: developers.openai.com
    sources:
      - {title: one, url: https://developers.openai.com/api/docs/models, type: documentation}
      - {title: duplicate, url: https://developers.openai.com/api/docs/models, type: documentation}
""",
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="duplicate"):
        load_manifest(path)


def test_expansion_manifest_registers_anthropic_before_gemini_without_activating_it() -> None:
    manifest = load_manifest(EXPANSION_MANIFEST)

    assert manifest.review_status == "pending_source_review"
    assert manifest.source_count == 8
    assert [candidate.collection.value for candidate in manifest.candidates[:4]] == [
        "anthropic",
        "anthropic",
        "anthropic",
        "anthropic",
    ]
    assert {candidate.collection.value for candidate in manifest.candidates} == {
        "anthropic",
        "gemini",
    }
