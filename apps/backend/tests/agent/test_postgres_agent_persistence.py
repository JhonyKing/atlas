from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from atlas.agent.checkpoints import PostgresCheckpointRepository
from atlas.agent.events import AgentRunEvent
from atlas.agent.planning import validate_plan
from atlas.agent.state import AtlasState
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest
from atlas.persistence.agent_runs import PostgresAgentEventStore, PostgresAgentRunRepository


class Result:
    def __init__(
        self,
        row: tuple[Any, ...] | None = None,
        rows: list[tuple[Any, ...]] | None = None,
    ):
        self.row = row
        self.rows = rows or []

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self) -> None:
        self.plan_row: tuple[Any, ...] | None = None
        self.run_row: tuple[Any, ...] | None = None
        self.checkpoint_row: tuple[Any, ...] | None = None
        self.events: list[AgentRunEvent] = []
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1

    def execute(self, sql: str, params=()):
        if "FROM atlas.agent_plans WHERE plan_hash" in sql:
            return Result(self.plan_row)
        if "FROM atlas.agent_runs AS r" in sql:
            return Result(self.run_row)
        if "SELECT id FROM atlas.agent_plans" in sql:
            return Result((uuid4(),))
        if "FROM atlas.agent_run_events" in sql and "max(sequence)" in sql:
            return Result((len(self.events) + 1,))
        if "FROM atlas.agent_run_events" in sql and "sequence >" in sql:
            return Result(
                rows=[
                    (
                        event.run_id,
                        event.sequence,
                        event.event_type,
                        event.occurred_at,
                        event.correlation_id,
                        event.tool_id,
                        event.tool_version,
                        event.call_id,
                        event.status,
                        list(event.evidence_ids),
                        list(event.artifact_ids),
                        event.error_category,
                        event.trace_id,
                    )
                    for event in self.events
                    if event.sequence > params[1]
                ]
            )
        if "INSERT INTO atlas.agent_run_events" in sql:
            self.events.append(
                AgentRunEvent(
                    run_id=params[0],
                    sequence=params[1],
                    event_type=params[2],
                    status=params[3],
                    call_id=params[4],
                    tool_id=params[5],
                    tool_version=params[6],
                    evidence_ids=tuple(params[7]),
                    artifact_ids=tuple(params[8]),
                    error_category=params[9],
                    correlation_id=params[10],
                    trace_id=params[11],
                    occurred_at=params[12],
                )
            )
            return Result()
        if "FROM atlas.agent_checkpoints" in sql:
            return Result(self.checkpoint_row)
        if "INSERT INTO atlas.agent_checkpoints" in sql:
            now = datetime.now(UTC)
            safe = getattr(params[5], "obj", params[5])
            self.checkpoint_row = (
                uuid4(),
                params[0],
                params[2],
                params[3],
                params[4],
                safe,
                now,
                params[6],
            )
            return Result((self.checkpoint_row[0], now, params[6]))
        return Result()


def _plan():
    return validate_plan(
        catalog=ToolCatalog.default(),
        request="How does LangGraph persist state?",
        locale="en-US",
        steps=(
            ToolCallRequest(
                tool_id="cited_answer",
                tool_version="1.0.0",
                arguments={"question": "How does LangGraph persist state?"},
            ),
        ),
    )


def test_postgres_agent_repository_round_trips_plan_and_run() -> None:
    connection = FakeConnection()
    plan = _plan()
    connection.plan_row = (
        plan.run_id,
        plan.request,
        plan.locale,
        plan.model_label,
        [step.model_dump(mode="json") for step in plan.steps],
        list(plan.risk_summary),
        plan.budget,
        plan.expires_at,
        plan.plan_hash,
    )
    repository = PostgresAgentRunRepository(connection)  # type: ignore[arg-type]

    repository.save_plan(plan)
    loaded = repository.get_plan(plan.plan_hash)

    assert loaded is not None
    assert loaded.plan_hash == plan.plan_hash
    assert loaded.steps[0].tool_id == "cited_answer"
    assert connection.commits == 1


def test_postgres_event_store_preserves_sequence_and_reconnect() -> None:
    connection = FakeConnection()
    store = PostgresAgentEventStore(connection)  # type: ignore[arg-type]
    run_id = uuid4()

    store.emit(run_id, "run.accepted", status="accepted")
    store.emit(run_id, "run.completed", status="completed")

    assert [event.sequence for event in store.list(run_id, after_sequence=1)] == [2]


def test_postgres_checkpoint_round_trip_rejects_changed_replay_state() -> None:
    connection = FakeConnection()
    repository = PostgresCheckpointRepository(connection)  # type: ignore[arg-type]
    thread_id = uuid4()
    state = AtlasState(thread_id=thread_id, request="first")

    checkpoint = repository.save(state, node="plan", replay_key="r1")
    assert repository.resume(thread_id, replay_key="r1").checkpoint_id == checkpoint.checkpoint_id
    try:
        repository.save(
            state.model_copy(update={"state_version": 2}), node="plan", replay_key="r1"
        )
    except Exception as exc:
        assert "replay key" in str(exc)
    else:
        raise AssertionError("changed replay state must be rejected")
