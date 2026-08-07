from atlas.retrieval.query import build_query_rewrite


def test_rewrite_never_changes_the_original_or_creates_a_destination() -> None:
    rewrite = build_query_rewrite(
        "OpenAI API",
        aliases={"openai": ("Responses API", "javascript", "https://evil.example")},
    )
    assert rewrite.original == "OpenAI API"
    assert rewrite.terms == ("Responses API", "javascript")
