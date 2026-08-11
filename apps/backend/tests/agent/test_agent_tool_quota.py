from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from atlas.persistence.agent_quota import (
    AgentToolQuotaConflict,
    AgentToolQuotaExceeded,
    InMemoryAgentToolQuotaRepository,
)


def test_agent_tool_quota_replays_without_consuming_a_second_unit() -> None:
    quota = InMemoryAgentToolQuotaRepository(limit=2, window=timedelta(hours=24))
    observed_at = datetime(2026, 8, 10, 12, tzinfo=UTC)
    run_id = UUID("00000000-0000-0000-0000-000000000001")

    first = quota.reserve(
        "visitor-a",
        "private_delete",
        "operation-key-001",
        run_id,
        "step-0",
        "a" * 64,
        now=observed_at,
    )
    replay = quota.reserve(
        "visitor-a",
        "private_delete",
        "operation-key-001",
        run_id,
        "step-0",
        "a" * 64,
        now=observed_at + timedelta(minutes=1),
    )

    assert first.remaining == replay.remaining == 1
    assert first.is_new is True
    assert replay.is_new is False


def test_agent_tool_quota_rejects_key_reuse_and_new_calls_over_the_limit() -> None:
    quota = InMemoryAgentToolQuotaRepository(limit=1, window=timedelta(hours=24))
    observed_at = datetime(2026, 8, 10, 12, tzinfo=UTC)
    run_id = UUID("00000000-0000-0000-0000-000000000001")
    quota.reserve(
        "visitor-a",
        "private_delete",
        "operation-key-001",
        run_id,
        "step-0",
        "a" * 64,
        now=observed_at,
    )

    with pytest.raises(AgentToolQuotaConflict):
        quota.reserve(
            "visitor-a",
            "private_delete",
            "operation-key-001",
            run_id,
            "step-0",
            "b" * 64,
            now=observed_at,
        )
    with pytest.raises(AgentToolQuotaExceeded) as exceeded:
        quota.reserve(
            "visitor-a",
            "private_delete",
            "operation-key-002",
            UUID("00000000-0000-0000-0000-000000000002"),
            "step-0",
            "c" * 64,
            now=observed_at,
        )

    assert exceeded.value.retry_at == observed_at + timedelta(hours=24)
