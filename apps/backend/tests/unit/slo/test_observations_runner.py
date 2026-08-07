from atlas.slo import SLOMeasurement
from atlas.slo.observations import PoolIndexObservation
from atlas.slo.runner import run_workload


def test_pool_index_observation_is_explicitly_measured() -> None:
    observation = PoolIndexObservation(10, 3, "retrieval", "idx_chunks_embedding", 12.5, "test")
    observation.validate()
    assert observation.measured is True


def test_runner_applies_the_same_fail_closed_gate_to_each_workload() -> None:
    results = run_workload(
        [("read", 10), ("answer", 10)],
        SLOMeasurement(0.999, 0.001, 8, 1, 120, 0.97, 1, 2),
    )
    assert all(result.passed for result in results)
