"""Independent temporal and version constraints for comparison branches."""

from __future__ import annotations

from datetime import date


def observation_matches_constraints(
    *,
    observed_date: date,
    observed_version: str | None,
    date_from: date | None,
    date_to: date | None,
    requested_version: str | None,
) -> bool:
    if date_from is not None and observed_date < date_from:
        return False
    if date_to is not None and observed_date > date_to:
        return False
    return requested_version is None or observed_version == requested_version
