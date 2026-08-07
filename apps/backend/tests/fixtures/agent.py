"""Deterministic Feature 006 fixtures shared by route/checkpoint/review tests."""

from datetime import UTC, datetime
from uuid import UUID

from atlas.agent.state import AtlasState

FIXED_NOW = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
FIXED_THREAD = UUID("00000000-0000-0000-0000-000000000006")


def fixture_state(request: str = "How does LangGraph work?") -> AtlasState:
    return AtlasState(thread_id=FIXED_THREAD, request=request, language="en-US")
