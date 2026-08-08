from uuid import uuid4

from atlas.agent.events import AgentRunEvent, EventSequenceError, InMemoryEventStore


def test_events_are_ordered_and_reconnectable() -> None:
    run_id = uuid4()
    store = InMemoryEventStore()
    store.emit(run_id, "run.accepted", status="accepted")
    store.emit(run_id, "run.completed", status="completed")
    assert [event.sequence for event in store.list(run_id, after_sequence=1)] == [2]
    try:
        store.append(
            AgentRunEvent(run_id=run_id, sequence=4, event_type="run.failed", status="failed")
        )
    except EventSequenceError:
        return
    raise AssertionError("event sequence gaps must fail closed")
