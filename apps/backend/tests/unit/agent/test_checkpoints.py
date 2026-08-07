from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from atlas.agent.checkpoints import CheckpointConflict, InMemoryCheckpointRepository
from atlas.agent.state import AtlasState


def test_checkpoint_resume_is_idempotent_and_content_safe() -> None:
    repository = InMemoryCheckpointRepository()
    thread_id = uuid4()
    state = AtlasState(thread_id=thread_id, request="What is LangGraph?", language="en-US")
    checkpoint = repository.save(state, node="classify", replay_key="r1")
    assert repository.resume(thread_id, replay_key="r1").checkpoint_id == checkpoint.checkpoint_id
    assert "What is LangGraph?" not in checkpoint.safe_summary


def test_duplicate_replay_with_different_state_is_rejected() -> None:
    repository = InMemoryCheckpointRepository()
    thread_id = uuid4()
    repository.save(
        AtlasState(thread_id=thread_id, request="first"), node="classify", replay_key="r1"
    )
    with pytest.raises(CheckpointConflict):
        repository.save(
            AtlasState(thread_id=thread_id, request="second"), node="classify", replay_key="r1"
        )


def test_resume_claim_is_single_use_and_expiry_is_enforced() -> None:
    now = datetime(2026, 8, 6, tzinfo=UTC)
    repository = InMemoryCheckpointRepository(ttl_hours=1, now=lambda: now)
    state = AtlasState(thread_id=uuid4(), request="first")
    repository.save(state, node="classify", replay_key="r1")
    assert repository.claim_resume(state.thread_id, replay_key="r1") is True
    assert repository.claim_resume(state.thread_id, replay_key="r1") is False
    clock = [now]
    expired = InMemoryCheckpointRepository(ttl_hours=1, now=lambda: clock[0])
    expired.save(state, node="classify", replay_key="r1")
    clock[0] = now + timedelta(hours=2)
    with pytest.raises(Exception, match="expired"):
        expired.resume(state.thread_id, replay_key="r1")


def test_resume_rejects_tampered_safe_summary() -> None:
    repository = InMemoryCheckpointRepository()
    state = AtlasState(thread_id=uuid4(), request="first")
    checkpoint = repository.save(state, node="classify", replay_key="r1")
    checkpoint.safe_summary["node"] = "tampered"
    with pytest.raises(Exception, match="integrity"):
        repository.resume(state.thread_id, replay_key="r1")
