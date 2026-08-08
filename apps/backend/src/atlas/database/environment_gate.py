"""Fail-closed checks before a Supabase migration write."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from atlas.database.migration_evidence import PROJECT_REF

Environment = Literal["development", "staging", "production", "unknown"]


class EnvironmentGateError(RuntimeError):
    """Raised when remote metadata does not permit a migration write."""


@dataclass(frozen=True)
class EnvironmentGate:
    """Remote metadata required to decide whether a write is safe."""

    project_ref: str
    environment: Environment
    contains_existing_data: bool
    owner_confirmed: bool = False

    def assert_write_allowed(self) -> None:
        """Raise unless this project is explicitly safe for the first migration write."""

        if self.project_ref != PROJECT_REF:
            raise EnvironmentGateError(
                f"Refusing write: expected project {PROJECT_REF}, got {self.project_ref}"
            )
        if self.environment in {"production", "unknown"}:
            raise EnvironmentGateError(
                f"Refusing write: environment {self.environment!r} requires explicit review"
            )
        if self.contains_existing_data and not self.owner_confirmed:
            raise EnvironmentGateError(
                "Refusing write: existing data requires explicit owner confirmation"
            )

