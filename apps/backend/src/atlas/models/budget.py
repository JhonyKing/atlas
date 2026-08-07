"""Daily model-cost budget enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class BudgetLedger:
    daily_limit: float
    spent: dict[date, float] = field(default_factory=dict)

    def reserve(self, day: date, amount: float) -> None:
        if amount < 0:
            raise ValueError("amount cannot be negative")
        current = self.spent.get(day, 0.0)
        if current + amount > self.daily_limit:
            raise RuntimeError("daily model budget exceeded")
        self.spent[day] = round(current + amount, 8)

    def remaining(self, day: date) -> float:
        return max(0.0, self.daily_limit - self.spent.get(day, 0.0))
