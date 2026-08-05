"""Explicit, credential-safe LangSmith connectivity smoke test."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest


@pytest.mark.integration
def test_langsmith_api_is_reachable_when_explicitly_enabled() -> None:
    if os.getenv("ATLAS_LANGSMITH_SMOKE") != "1":
        pytest.skip("set ATLAS_LANGSMITH_SMOKE=1 to enable the network smoke test")
    if not os.getenv("LANGSMITH_API_KEY"):
        pytest.skip("LANGSMITH_API_KEY is required for the opt-in smoke test")

    from langsmith import Client

    client = Client(
        api_url=os.getenv("LANGSMITH_ENDPOINT") or None,
        api_key=os.environ["LANGSMITH_API_KEY"],
        workspace_id=os.getenv("LANGSMITH_WORKSPACE_ID") or None,
    )
    run_id = uuid4()
    client.create_run(
        id=run_id,
        name="atlas-langsmith-smoke",
        run_type="chain",
        inputs={"smoke": "opt-in"},
        outputs={"status": "created"},
        project_name=os.getenv("LANGSMITH_PROJECT", "atlas-ai"),
        tags=["atlas-smoke", "portfolio-test"],
        start_time=datetime.now(UTC),
        end_time=datetime.now(UTC),
    )
