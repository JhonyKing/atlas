import pytest

from atlas.agent.checkpoints import InMemoryCheckpointRepository
from atlas.agent.state import AtlasState


@pytest.mark.parametrize("job_kind", ["answer", "report", "ingestion", "evaluation"])
def test_resume_is_single_use_for_each_long_running_job_kind(job_kind: str) -> None:
    repository = InMemoryCheckpointRepository()
    state = AtlasState(request=f"fixture {job_kind}")
    repository.save(state, node=job_kind, replay_key=f"replay-{job_kind}")
    assert repository.claim_resume(state.thread_id, replay_key=f"replay-{job_kind}") is True
    assert repository.claim_resume(state.thread_id, replay_key=f"replay-{job_kind}") is False


def test_worker_failure_can_resume_from_the_same_checkpoint() -> None:
    repository = InMemoryCheckpointRepository()
    state = AtlasState(request="resume after worker failure")
    repository.save(state, node="retrieve", replay_key="worker-1")
    try:
        raise RuntimeError("simulated worker failure")
    except RuntimeError:
        assert repository.resume(state.thread_id, replay_key="worker-1").node == "retrieve"
