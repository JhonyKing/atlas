"""Effective-dated, provider-independent model pricing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class PriceVersion:
    id: str
    provider: str
    model: str
    input_per_million: float
    output_per_million: float
    effective_from: date
    effective_to: date | None = None

    def applies_on(self, day: date) -> bool:
        return self.effective_from <= day and (
            self.effective_to is None or day <= self.effective_to
        )


def select_price(prices: list[PriceVersion], provider: str, model: str, day: date) -> PriceVersion:
    matches = [
        price
        for price in prices
        if price.provider == provider and price.model == model and price.applies_on(day)
    ]
    if len(matches) != 1:
        raise ValueError("expected exactly one active price version")
    return matches[0]


def estimate_cost(price: PriceVersion, *, input_tokens: int, output_tokens: int) -> float:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts cannot be negative")
    return round(
        input_tokens * price.input_per_million / 1_000_000
        + output_tokens * price.output_per_million / 1_000_000,
        8,
    )
