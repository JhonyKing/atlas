from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from atlas.agent.checkpoints import PostgresCheckpointRepository
from atlas.agent.events import AgentRunEvent
from atlas.agent.planning import validate_plan
from atlas.agent.policy import issue_approval
from atlas.agent.state import AtlasState
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest
from atlas.persistence.agent_runs import (
    IdempotencyConflict,
    InMemoryAgentRunRepository,
    PostgresAgentEventStore,
    PostgresAgentRunRepository,
    PostgresIdempotencyStore,
)


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
        self.run_actor: str | None = None
        self.checkpoint_row: tuple[Any, ...] | None = None
        self.checkpoint_claim_row: tuple[Any, ...] | None = None
        self.approval_row: tuple[Any, ...] | None = None
        self.tool_call_row: tuple[Any, ...] | None = None
        self.idempotency_row: tuple[Any, ...] | None = None
        self.events: list[AgentRunEvent] = []
        self.commits = 0
        self.statements: list[str] = []

    def commit(self) -> None:
        self.commits += 1

    def execute(self, sql: str, params=()):
        self.statements.append(" ".join(sql.split()))
        if "FROM atlas.agent_plans WHERE plan_hash" in sql:
            return Result(self.plan_row)
        if "FROM atlas.agent_runs AS r" in sql:
            return Result(self.run_row)
        if "FROM atlas.agent_approvals" in sql:
            return Result(self.approval_row)
        if "FROM atlas.agent_tool_calls" in sql:
            return Result(self.tool_call_row)
        if "FROM atlas.agent_idempotency_records" in sql:
            if "response" in sql:
                return Result(self.idempotency_row)
            return Result((self.idempotency_row[0],) if self.idempotency_row else None)
        if "SELECT id FROM atlas.agent_plans" in sql:
            return Result((uuid4(),))
        if "INSERT INTO atlas.agent_runs" in sql:
            self.run_actor = str(params[2])
            return Result()
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
        if "INSERT INTO atlas.agent_approvals" in sql:
            self.approval_row = params
            return Result()
        if "INSERT INTO atlas.agent_tool_calls" in sql:
            self.tool_call_row = params
            return Result()
        if "INSERT INTO atlas.agent_idempotency_records" in sql:
            self.idempotency_row = (params[2], params[3].obj)
            return Result()
        if "INSERT INTO atlas.agent_checkpoint_claims" in sql:
            if self.checkpoint_claim_row is not None:
                return Result()
            self.checkpoint_claim_row = (uuid4(), params[0], params[1], params[2])
            return Result(self.checkpoint_claim_row[:1])
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


def test_postgres_agent_repository_persists_run_actor() -> None:
    connection = FakeConnection()
    plan = _plan()
    repository = PostgresAgentRunRepository(connection)  # type: ignore[arg-type]

    repository.save_plan(plan)
    connection.plan_row = (uuid4(),)
    repository.create_run(plan, actor_id="user-42")

    assert connection.run_actor == "user-42"


def test_postgres_create_run_keeps_existing_terminal_record() -> None:
    connection = FakeConnection()
    plan = _plan()
    repository = PostgresAgentRunRepository(connection)  # type: ignore[arg-type]
    connection.plan_row = (uuid4(),)
    connection.run_row = (
        plan.run_id,
        plan.request,
        plan.locale,
        plan.plan_hash,
        "user-42",
        "completed",
        datetime.now(UTC),
        {"event_count": 4},
    )

    record = repository.create_run(plan, actor_id="different-user")

    assert record.status == "completed"
    assert record.actor_id == "user-42"
    assert not any(
        "INSERT INTO atlas.agent_runs" in statement for statement in connection.statements
    )


def test_postgres_event_store_preserves_sequence_and_reconnect() -> None:
    connection = FakeConnection()
    store = PostgresAgentEventStore(connection)  # type: ignore[arg-type]
    run_id = uuid4()

    store.emit(run_id, "run.accepted", status="accepted")
    store.emit(run_id, "run.completed", status="completed")

    assert [event.sequence for event in store.list(run_id, after_sequence=1)] == [2]


def test_postgres_event_store_locks_run_before_allocating_sequence() -> None:
    connection = FakeConnection()
    store = PostgresAgentEventStore(connection)  # type: ignore[arg-type]
    run_id = uuid4()

    store.emit(run_id, "run.accepted", status="accepted")

    lock_index = next(
        index for index, statement in enumerate(connection.statements)
        if "pg_advisory_xact_lock" in statement
    )
    max_index = next(
        index for index, statement in enumerate(connection.statements)
        if "max(sequence)" in statement
    )
    assert lock_index < max_index


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


def test_postgres_checkpoint_claim_is_cross_repository_idempotent() -> None:
    connection = FakeConnection()
    first = PostgresCheckpointRepository(connection)  # type: ignore[arg-type]
    second = PostgresCheckpointRepository(connection)  # type: ignore[arg-type]
    state = AtlasState(thread_id=uuid4(), request="first")
    first.save(state, node="plan", replay_key="r1")

    assert first.claim_resume(state.thread_id, replay_key="r1") is True
    assert second.claim_resume(state.thread_id, replay_key="r1") is False


def test_postgres_repository_persists_approval_and_tool_call_records() -> None:
    connection = FakeConnection()
    repository = PostgresAgentRunRepository(connection)  # type: ignore[arg-type]
    plan = _plan()
    approval = issue_approval(
        plan,
        call_id="step-0",
        actor_id="user-1",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "resource-1"},
    )

    repository.save_approval(approval)
    connection.approval_row = (
        approval.approval_id,
        approval.run_id,
        approval.call_id,
        approval.actor_id,
        approval.tool_id,
        approval.tool_version,
        approval.arguments_hash,
        approval.target_resource,
        approval.decision,
        approval.decision_key,
        approval.expires_at,
    )
    assert repository.get_approval(approval.approval_id) == approval

    repository.save_tool_call(
        plan.run_id,
        call_id="step-0",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments_hash="a" * 64,
        status="completed",
        evidence_ids=("ev-1",),
    )
    connection.tool_call_row = (
        plan.run_id,
        "step-0",
        "private_delete",
        "1.0.0",
        "a" * 64,
        "completed",
        ["ev-1"],
        [],
        None,
        None,
        datetime.now(UTC),
    )
    record = repository.get_tool_call(plan.run_id, "step-0")
    assert record is not None
    assert record["status"] == "completed"
    assert record["evidence_ids"] == ("ev-1",)


def test_postgres_idempotency_store_replays_and_rejects_conflicts() -> None:
    connection = FakeConnection()
    store = PostgresIdempotencyStore(connection)  # type: ignore[arg-type]
    response = {"run_id": "run-1", "status": "completed"}
    fingerprint = "a" * 64

    store.save("agent.run:owner-1", "request-key-1", fingerprint, response)
    connection.idempotency_row = (fingerprint, response)
    assert store.get("agent.run:owner-1", "request-key-1", fingerprint) == response
    try:
        store.get("agent.run:owner-1", "request-key-1", "b" * 64)
    except IdempotencyConflict:
        pass
    else:
        raise AssertionError("conflicting fingerprints must be rejected")


def test_inmemory_repository_keeps_tool_call_and_approval_records() -> None:
    repository = InMemoryAgentRunRepository()
    plan = _plan()
    repository.save_plan(plan)
    approval = issue_approval(
        plan,
        call_id="step-0",
        actor_id="user-1",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "resource-1"},
    )
    repository.save_approval(approval)
    repository.save_tool_call(
        plan.run_id,
        call_id="step-0",
        tool_id="cited_answer",
        tool_version="1.0.0",
        arguments_hash="a" * 64,
        status="completed",
        evidence_ids=("ev-1",),
        artifact_ids=(),
    )

    assert repository.get_approval(approval.approval_id) == approval
    assert repository.get_tool_call(plan.run_id, "step-0")["status"] == "completed"
