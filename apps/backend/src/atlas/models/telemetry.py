"""Content-free model cost telemetry records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CostRecord:
    run_id: str
    provider: str
    model: str
    price_version: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    budget_bucket: str

    def as_metadata(self) -> dict[str, str | int | float]:
        return {
            "run_id": self.run_id,
            "provider": self.provider,
            "model": self.model,
            "price_version": self.price_version,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "estimated_cost": self.estimated_cost,
            "budget_bucket": self.budget_bucket,
        }
