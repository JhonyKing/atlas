from atlas.retrieval.embedding_benchmark import benchmark_embedding_profiles


def test_multilingual_profile_benchmark_records_fallback_and_quality() -> None:
    relevant = [{"es"}, {"en"}]
    results = benchmark_embedding_profiles(
        {
            "baseline-multilingual": [["es"], ["en"]],
            "language-aware-v1": [["es"], ["en"]],
        },
        relevant,
        fallback_profile="baseline-multilingual",
    )
    assert [(item.profile, item.hit_at_5, item.mrr) for item in results] == [
        ("baseline-multilingual", 1.0, 1.0),
        ("language-aware-v1", 1.0, 1.0),
    ]
    assert results[0].fallback_cases == 2
