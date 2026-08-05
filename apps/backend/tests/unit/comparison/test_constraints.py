from datetime import date

from atlas.comparison.constraints import observation_matches_constraints


def test_temporal_and_version_constraints_are_applied_independently() -> None:
    assert observation_matches_constraints(
        observed_date=date(2026, 8, 5),
        observed_version="1.0",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 8, 5),
        requested_version="1.0",
    )
    assert not observation_matches_constraints(
        observed_date=date(2024, 1, 1),
        observed_version="1.0",
        date_from=date(2026, 1, 1),
        date_to=None,
        requested_version="1.0",
    )
    assert not observation_matches_constraints(
        observed_date=date(2026, 8, 5),
        observed_version="gpt-3.5",
        date_from=None,
        date_to=None,
        requested_version="gpt-4",
    )
