"""Tests for fail-closed Supabase environment classification."""

from typing import cast

import pytest

from atlas.database.environment_gate import Environment, EnvironmentGate, EnvironmentGateError
from atlas.database.migration_evidence import PROJECT_REF


def test_development_without_existing_data_allows_write() -> None:
    EnvironmentGate(PROJECT_REF, "development", contains_existing_data=False).assert_write_allowed()


@pytest.mark.parametrize("environment", ["production", "unknown"])
def test_production_or_unknown_environment_blocks_write(environment: str) -> None:
    with pytest.raises(EnvironmentGateError, match="environment"):
        EnvironmentGate(
            PROJECT_REF, cast(Environment, environment), contains_existing_data=False
        ).assert_write_allowed()


def test_existing_data_requires_owner_confirmation() -> None:
    gate = EnvironmentGate(PROJECT_REF, "development", contains_existing_data=True)

    with pytest.raises(EnvironmentGateError, match="existing data"):
        gate.assert_write_allowed()


def test_wrong_project_ref_blocks_write() -> None:
    with pytest.raises(EnvironmentGateError, match="expected project"):
        EnvironmentGate(
            "wrong-project", "development", contains_existing_data=False
        ).assert_write_allowed()
