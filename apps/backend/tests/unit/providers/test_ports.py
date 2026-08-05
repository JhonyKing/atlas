from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import HttpUrl

from atlas.domain import AnswerStatus, Evidence, Question, SourceType
from atlas.providers.ports import (
    AnswerGenerator,
    Clock,
    EmbeddingProvider,
    FetchedSource,
    ModelPrice,
    PriceTable,
    SourceFetcher,
)
from tests.fakes import (
    DeterministicAnswerGenerator,
    DeterministicEmbeddingProvider,
    FixedClock,
    FixtureSourceFetcher,
    StaticPriceTable,
)

NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)


def sample_evidence() -> Evidence:
    return Evidence(
        id=uuid4(),
        source_title="Official docs",
        publisher="Example",
        canonical_url=HttpUrl("https://example.com/docs"),
        excerpt="The official behavior is documented here.",
        captured_at=NOW,
        source_type=SourceType.DOCUMENTATION,
    )


@pytest.mark.asyncio
async def test_deterministic_answer_generator_implements_provider_port() -> None:
    fake = DeterministicAnswerGenerator()
    question = Question(text="What does the official documentation say?")

    assert isinstance(fake, AnswerGenerator)
    generator: AnswerGenerator = fake
    draft = await generator.generate(question, [sample_evidence()])

    assert draft.answer_status is AnswerStatus.COMPLETE
    assert len(draft.claims) == 1
    assert fake.calls == 1


@pytest.mark.asyncio
async def test_embedding_fake_is_repeatable_and_preserves_dimension() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=8)

    assert isinstance(provider, EmbeddingProvider)
    first = await provider.embed(["same text", "other text"])
    second = await provider.embed(["same text", "other text"])

    assert first == second
    assert len(first) == 2
    assert all(len(vector) == 8 for vector in first)


def test_clock_and_price_table_are_deterministic_and_effective_dated() -> None:
    clock = FixedClock(NOW)
    prices = StaticPriceTable(
        [
            ModelPrice(
                model_id="gpt-5.6-luna",
                effective_from=datetime(2026, 1, 1, tzinfo=UTC),
                input_per_million=Decimal("1.00"),
                output_per_million=Decimal("4.00"),
            ),
            ModelPrice(
                model_id="gpt-5.6-luna",
                effective_from=datetime(2026, 8, 1, tzinfo=UTC),
                input_per_million=Decimal("1.25"),
                output_per_million=Decimal("5.00"),
            ),
        ]
    )

    assert isinstance(clock, Clock)
    assert isinstance(prices, PriceTable)
    assert clock.now() == NOW
    price = prices.get("gpt-5.6-luna", NOW)
    assert price is not None
    assert price.input_per_million == Decimal("1.25")
    assert prices.get("unknown", NOW) is None


@pytest.mark.asyncio
async def test_fixture_source_fetcher_never_calls_the_network() -> None:
    fixture = FetchedSource(
        requested_url="https://example.com/docs",
        final_url="https://example.com/docs",
        content=b"# Official docs",
        content_type="text/markdown",
        fetched_at=NOW,
    )
    fetcher = FixtureSourceFetcher({fixture.requested_url: fixture})

    assert isinstance(fetcher, SourceFetcher)
    result = await fetcher.fetch(fixture.requested_url)

    assert result is fixture
