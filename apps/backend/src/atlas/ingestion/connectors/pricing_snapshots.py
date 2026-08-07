"""Effective-dated model and pricing snapshots."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PricingSnapshot:
    model: str
    effective_date: str
    input_price: float
    output_price: float
    outcome: str


class PricingSnapshotStore:
    def __init__(self) -> None:
        self._history: dict[str, list[PricingSnapshot]] = {}

    def record(
        self, model: str, *, effective_date: str, input_price: float, output_price: float
    ) -> PricingSnapshot:
        previous = self._history.get(model, [])
        outcome = (
            "unchanged"
            if previous
            and (
                previous[-1].input_price == input_price
                and previous[-1].output_price == output_price
                and previous[-1].effective_date == effective_date
            )
            else ("changed" if previous else "new")
        )
        snapshot = PricingSnapshot(model, effective_date, input_price, output_price, outcome)
        if outcome != "unchanged":
            self._history.setdefault(model, []).append(snapshot)
        return snapshot

    def history(self, model: str) -> list[PricingSnapshot]:
        return list(self._history.get(model, []))
