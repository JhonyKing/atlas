"""Evidence records for pool/index observations without capacity claims."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PoolIndexObservation:
    database_pool_size: int
    observed_in_use: int
    query_name: str
    index_name: str | None
    duration_ms: float
    environment: str
    measured: bool = True

    def validate(self) -> None:
        if self.database_pool_size < 1 or not 0 <= self.observed_in_use <= self.database_pool_size:
            raise ValueError("pool usage is outside the configured bounds")
        if self.duration_ms < 0:
            raise ValueError("duration cannot be negative")
        if not self.query_name.strip() or not self.environment.strip():
            raise ValueError("query and environment are required")
