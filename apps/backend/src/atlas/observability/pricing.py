"""Effective-dated model prices and deterministic token-cost accounting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from atlas.providers.ports import ModelPrice

_MILLION: Final[Decimal] = Decimal(1_000_000)
_MICRO_USD: Final[Decimal] = Decimal("0.000001")


@dataclass(frozen=True, slots=True)
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0

    def __post_init__(self) -> None:
        counts = (
            self.input_tokens,
            self.output_tokens,
            self.reasoning_tokens,
            self.cached_tokens,
            self.cache_write_tokens,
        )
        if any(value < 0 for value in counts):
            raise ValueError("token counts must not be negative")
        if self.cached_tokens > self.input_tokens:
            raise ValueError("cached tokens cannot exceed input tokens")


@dataclass(frozen=True, slots=True)
class CostEstimate:
    total_usd: Decimal
    price_table_version: str
    model_id: str


@dataclass(slots=True)
class CostMetrics:
    """Process-local aggregate cost counters; no request or source content is retained."""

    request_count: int = 0
    total_usd: Decimal = Decimal("0")

    def observe(self, estimate: CostEstimate) -> None:
        self.request_count += 1
        self.total_usd += estimate.total_usd

    def snapshot(self) -> dict[str, int | Decimal]:
        return {
            "request_count": self.request_count,
            "total_usd": self.total_usd.quantize(_MICRO_USD, rounding=ROUND_HALF_UP),
        }


class MissingPriceError(LookupError):
    """Raised when a model or token class has no effective price."""


class EffectivePriceTable:
    """Immutable price table selecting the latest entry effective at observation time."""

    def __init__(self, *, version: str, prices: tuple[ModelPrice, ...]) -> None:
        if not version.strip():
            raise ValueError("price table version must not be blank")
        self.version = version
        self._prices = tuple(prices)

    def get(self, model_id: str, observed_at: datetime) -> ModelPrice | None:
        observed = _aware(observed_at)
        candidates = [
            price
            for price in self._prices
            if price.model_id == model_id and _aware(price.effective_from) <= observed
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda price: _aware(price.effective_from))


def estimate_cost(
    table: EffectivePriceTable,
    model_id: str,
    usage: TokenUsage,
    *,
    observed_at: datetime,
) -> CostEstimate:
    """Calculate a historical estimate without mutating the price table or usage."""

    price = table.get(model_id, observed_at)
    if price is None:
        raise MissingPriceError(f"no price is effective for {model_id}")

    input_tokens = usage.input_tokens - usage.cached_tokens
    total = _charge(input_tokens, price.input_per_million)
    total += _charge(
        usage.cached_tokens,
        price.cache_read_per_million or price.input_per_million,
    )
    total += _charge(
        usage.cache_write_tokens,
        price.cache_write_per_million or price.input_per_million,
    )
    total += _charge(usage.output_tokens, price.output_per_million)
    total += _charge(
        usage.reasoning_tokens,
        price.reasoning_per_million or price.output_per_million,
    )
    return CostEstimate(
        total_usd=total.quantize(_MICRO_USD, rounding=ROUND_HALF_UP),
        price_table_version=table.version,
        model_id=model_id,
    )


def _charge(tokens: int, price_per_million: Decimal) -> Decimal:
    return (Decimal(tokens) / _MILLION) * price_per_million


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
