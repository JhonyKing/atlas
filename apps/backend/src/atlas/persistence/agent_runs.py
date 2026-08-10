"""In-memory durable-port substitute for agent plans, calls, and ordered events."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from typing import Any, Protocol
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb

from atlas.agent.events import AgentRunEvent, InMemoryEventStore
from atlas.agent.planning import AgentPlan
from atlas.agent.policy import Approval
from atlas.agent.tools.schemas import ToolCallRequest


@dataclass(frozen=True, slots=True)
class AgentRunRecord:
    run_id: UUID
    request: str
    locale: str
    plan_hash: str
    actor_id: str
    status: str
    created_at: datetime
    output: dict[str, object]


class AgentRunRepository(Protocol):
    events: Any

    def save_plan(self, plan: AgentPlan) -> AgentPlan: ...

    def get_plan(self, plan_hash: str) -> AgentPlan | None: ...

    def create_run(self, plan: AgentPlan, *, actor_id: str = "anonymous") -> AgentRunRecord: ...

    def update(
        self, run_id: UUID, *, status: str, output: dict[str, object] | None = None
    ) -> AgentRunRecord: ...

    def get(self, run_id: UUID) -> AgentRunRecord | None: ...

    def list_events(self, run_id: UUID, after_sequence: int = 0) -> tuple[AgentRunEvent, ...]: ...

    def save_approval(self, approval: Approval) -> None: ...

    def get_approval(self, approval_id: UUID) -> Approval | None: ...

    def save_tool_call(
        self,
        run_id: UUID,
        *,
        call_id: str,
        tool_id: str,
        tool_version: str,
        arguments_hash: str,
        status: str,
        evidence_ids: tuple[str, ...] = (),
        artifact_ids: tuple[str, ...] = (),
        error_category: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> None: ...

    def get_tool_call(self, run_id: UUID, call_id: str) -> dict[str, object] | None: ...


class IdempotencyConflict(ValueError):
    """A key was reused with a different request fingerprint."""


class AgentIdempotencyStore(Protocol):
    def get(self, scope: str, key: str, fingerprint: str) -> dict[str, object] | None: ...

    def save(
        self, scope: str, key: str, fingerprint: str, response: Mapping[str, object]
    ) -> None: ...


class InMemoryIdempotencyStore:
    """Small process-local replay store used until the durable idempotency tables are wired."""

    owner_scoped = False

    def __init__(self) -> None:
        self._items: dict[tuple[str, str], tuple[str, dict[str, object]]] = {}
        self._lock = RLock()

    def get(self, scope: str, key: str, fingerprint: str) -> dict[str, object] | None:
        with self._lock:
            item = self._items.get((scope, key))
            if item is None:
                return None
            if item[0] != fingerprint:
                raise IdempotencyConflict("idempotency key conflicts with another request")
            return dict(item[1])

    def save(
        self, scope: str, key: str, fingerprint: str, response: Mapping[str, object]
    ) -> None:
        with self._lock:
            existing = self._items.get((scope, key))
            if existing is not None and existing[0] != fingerprint:
                raise IdempotencyConflict("idempotency key conflicts with another request")
            self._items[(scope, key)] = (fingerprint, dict(response))


class PostgresIdempotencyStore:
    """Durable replay store for non-development runtimes."""

    owner_scoped = True

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get(self, scope: str, key: str, fingerprint: str) -> dict[str, object] | None:
        row = self._connection.execute(
            """
            SELECT fingerprint, response
            FROM atlas.agent_idempotency_records
            WHERE scope = %s AND idempotency_key = %s
            """,
            (scope, key),
        ).fetchone()
        if row is None:
            return None
        if str(row[0]).strip() != fingerprint:
            raise IdempotencyConflict("idempotency key conflicts with another request")
        return dict(row[1] or {})

    def save(
        self, scope: str, key: str, fingerprint: str, response: Mapping[str, object]
    ) -> None:
        existing = self._connection.execute(
            """
            SELECT fingerprint
            FROM atlas.agent_idempotency_records
            WHERE scope = %s AND idempotency_key = %s
            """,
            (scope, key),
        ).fetchone()
        if existing is not None and str(existing[0]).strip() != fingerprint:
            raise IdempotencyConflict("idempotency key conflicts with another request")
        if existing is None:
            self._connection.execute(
                """
                INSERT INTO atlas.agent_idempotency_records(
                  scope, idempotency_key, fingerprint, response
                ) VALUES (%s, %s, %s, %s)
                """,
                (scope, key, fingerprint, Jsonb(dict(response))),
            )
            self._connection.commit()


class InMemoryAgentRunRepository:
    def __init__(self, *, events: InMemoryEventStore | None = None) -> None:
        self.events = events or InMemoryEventStore()
        self._runs: dict[UUID, AgentRunRecord] = {}
        self._plans: dict[str, AgentPlan] = {}
        self._approvals: dict[UUID, Approval] = {}
        self._tool_calls: dict[tuple[UUID, str], dict[str, object]] = {}

    def save_plan(self, plan: AgentPlan) -> AgentPlan:
        self._plans[plan.plan_hash] = plan
        return plan

    def get_plan(self, plan_hash: str) -> AgentPlan | None:
        return self._plans.get(plan_hash)

    def create_run(self, plan: AgentPlan, *, actor_id: str = "anonymous") -> AgentRunRecord:
        existing = self._runs.get(plan.run_id)
        if existing is not None:
            return existing
        record = AgentRunRecord(
            plan.run_id,
            plan.request,
            plan.locale,
            plan.plan_hash,
            actor_id,
            "accepted",
            datetime.now(UTC),
            {},
        )
        self._runs[plan.run_id] = record
        return record

    def update(
        self, run_id: UUID, *, status: str, output: dict[str, object] | None = None
    ) -> AgentRunRecord:
        current = self._runs[run_id]
        updated = AgentRunRecord(
            current.run_id,
            current.request,
            current.locale,
            current.plan_hash,
            current.actor_id,
            status,
            current.created_at,
            output or current.output,
        )
        self._runs[run_id] = updated
        return updated

    def get(self, run_id: UUID) -> AgentRunRecord | None:
        return self._runs.get(run_id)

    def list_events(self, run_id: UUID, after_sequence: int = 0) -> tuple[AgentRunEvent, ...]:
        return self.events.list(run_id, after_sequence=after_sequence)

    def save_approval(self, approval: Approval) -> None:
        self._approvals[approval.approval_id] = approval

    def get_approval(self, approval_id: UUID) -> Approval | None:
        return self._approvals.get(approval_id)

    def save_tool_call(
        self,
        run_id: UUID,
        *,
        call_id: str,
        tool_id: str,
        tool_version: str,
        arguments_hash: str,
        status: str,
        evidence_ids: tuple[str, ...] = (),
        artifact_ids: tuple[str, ...] = (),
        error_category: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> None:
        self._tool_calls[(run_id, call_id)] = {
            "run_id": run_id,
            "call_id": call_id,
            "tool_id": tool_id,
            "tool_version": tool_version,
            "arguments_hash": arguments_hash,
            "status": status,
            "evidence_ids": evidence_ids,
            "artifact_ids": artifact_ids,
            "error_category": error_category,
            "started_at": started_at,
            "completed_at": completed_at,
        }

    def get_tool_call(self, run_id: UUID, call_id: str) -> dict[str, object] | None:
        return self._tool_calls.get((run_id, call_id))


class PostgresAgentEventStore:
    """Append-only PostgreSQL event store with the same API as the in-memory store."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def emit(
        self,
        run_id: UUID,
        event_type: str,
        *,
        status: str,
        **kwargs: object,
    ) -> AgentRunEvent:
        # Serialize sequence allocation per run across worker processes. The
        # transaction-scoped advisory lock keeps the existing append-only
        # schema while preventing two workers from selecting the same next
        # sequence concurrently.
        self._connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (str(run_id),),
        )
        sequence_row = self._connection.execute(
            "SELECT coalesce(max(sequence), 0) + 1 FROM atlas.agent_run_events WHERE run_id = %s",
            (run_id,),
        ).fetchone()
        sequence = int(sequence_row[0]) if sequence_row is not None else 1
        event = AgentRunEvent.model_validate(
            {
                "run_id": run_id,
                "sequence": sequence,
                "event_type": event_type,
                "status": status,
                **kwargs,
            }
        )
        self._connection.execute(
            """
            INSERT INTO atlas.agent_run_events(
              run_id, sequence, event_type, status, call_id, tool_id, tool_version,
              evidence_ids, artifact_ids, error_category, correlation_id, trace_id, occurred_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                event.run_id,
                event.sequence,
                event.event_type,
                event.status,
                event.call_id,
                event.tool_id,
                event.tool_version,
                list(event.evidence_ids),
                list(event.artifact_ids),
                event.error_category,
                event.correlation_id,
                event.trace_id,
                event.occurred_at,
            ),
        )
        self._connection.commit()
        return event

    def list(self, run_id: UUID, *, after_sequence: int = 0) -> tuple[AgentRunEvent, ...]:
        rows = self._connection.execute(
            """
            SELECT run_id, sequence, event_type, occurred_at, correlation_id, tool_id,
                   tool_version, call_id, status, evidence_ids, artifact_ids, error_category,
                   trace_id
            FROM atlas.agent_run_events
            WHERE run_id = %s AND sequence > %s
            ORDER BY sequence
            """,
            (run_id, after_sequence),
        ).fetchall()
        return tuple(
            AgentRunEvent.model_validate(
                {
                    "run_id": row[0],
                    "sequence": row[1],
                    "event_type": row[2],
                    "occurred_at": row[3],
                    "correlation_id": row[4],
                    "tool_id": row[5],
                    "tool_version": row[6],
                    "call_id": row[7],
                    "status": row[8],
                    "evidence_ids": tuple(row[9] or ()),
                    "artifact_ids": tuple(row[10] or ()),
                    "error_category": row[11],
                    "trace_id": row[12],
                }
            )
            for row in rows
        )


class PostgresAgentRunRepository:
    """Durable plan/run/event repository for the migration 0028 contract."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
        self.events = PostgresAgentEventStore(connection)

    def save_plan(self, plan: AgentPlan) -> AgentPlan:
        self._connection.execute(
            """
            INSERT INTO atlas.agent_plans(
              run_id, plan_hash, request, locale, model_label, steps, risk_summary,
              budget, expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (plan_hash) DO UPDATE SET
              request = EXCLUDED.request, steps = EXCLUDED.steps, budget = EXCLUDED.budget,
              expires_at = EXCLUDED.expires_at
            """,
            (
                plan.run_id,
                plan.plan_hash,
                plan.request,
                plan.locale,
                plan.model_label,
                Jsonb([step.model_dump(mode="json") for step in plan.steps]),
                Jsonb(list(plan.risk_summary)),
                Jsonb(plan.budget),
                plan.expires_at,
            ),
        )
        self._connection.commit()
        return plan

    def get_plan(self, plan_hash: str) -> AgentPlan | None:
        row = self._connection.execute(
            """
            SELECT run_id, request, locale, model_label, steps, risk_summary, budget,
                   expires_at, plan_hash
            FROM atlas.agent_plans WHERE plan_hash = %s
            """,
            (plan_hash,),
        ).fetchone()
        if row is None:
            return None
        return AgentPlan(
            run_id=row[0],
            request=row[1],
            locale=row[2],
            model_label=row[3],
            steps=tuple(ToolCallRequest.model_validate(value) for value in row[4]),
            risk_summary=tuple(row[5] or ()),
            budget=dict(row[6]),
            expires_at=row[7],
            plan_hash=row[8],
        )

    def create_run(self, plan: AgentPlan, *, actor_id: str = "anonymous") -> AgentRunRecord:
        plan_row = self._connection.execute(
            "SELECT id FROM atlas.agent_plans WHERE plan_hash = %s", (plan.plan_hash,)
        ).fetchone()
        if plan_row is None:
            raise KeyError("plan not found")
        existing = self.get(plan.run_id)
        if existing is not None:
            return existing
        created_at = datetime.now(UTC)
        self._connection.execute(
            """
            INSERT INTO atlas.agent_runs(
              id, plan_id, actor_id, status, output, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (plan.run_id, plan_row[0], actor_id, "accepted", Jsonb({}), created_at, created_at),
        )
        self._connection.commit()
        return AgentRunRecord(
            plan.run_id,
            plan.request,
            plan.locale,
            plan.plan_hash,
            actor_id,
            "accepted",
            created_at,
            {},
        )

    def update(
        self, run_id: UUID, *, status: str, output: dict[str, object] | None = None
    ) -> AgentRunRecord:
        current = self.get(run_id)
        if current is None:
            raise KeyError(run_id)
        resolved_output = output if output is not None else current.output
        self._connection.execute(
            """
            UPDATE atlas.agent_runs
            SET status = %s, output = %s, updated_at = now()
            WHERE id = %s
            """,
            (status, Jsonb(resolved_output), run_id),
        )
        self._connection.commit()
        return AgentRunRecord(
            current.run_id,
            current.request,
            current.locale,
            current.plan_hash,
            current.actor_id,
            status,
            current.created_at,
            resolved_output,
        )

    def get(self, run_id: UUID) -> AgentRunRecord | None:
        row = self._connection.execute(
            """
            SELECT r.id, p.request, p.locale, p.plan_hash, r.actor_id, r.status,
                   r.created_at, r.output
            FROM atlas.agent_runs AS r
            JOIN atlas.agent_plans AS p ON p.id = r.plan_id
            WHERE r.id = %s
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return AgentRunRecord(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], dict(row[7] or {})
        )

    def list_events(self, run_id: UUID, after_sequence: int = 0) -> tuple[AgentRunEvent, ...]:
        return self.events.list(run_id, after_sequence=after_sequence)

    def save_approval(self, approval: Approval) -> None:
        self._connection.execute(
            """
            INSERT INTO atlas.agent_approvals(
              approval_id, run_id, call_id, actor_id, tool_id, tool_version, arguments_hash,
              target_resource, decision, decision_key, expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id, call_id) DO UPDATE SET
              decision = EXCLUDED.decision, decision_key = EXCLUDED.decision_key,
              expires_at = EXCLUDED.expires_at
            """,
            (
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
            ),
        )
        self._connection.commit()

    def get_approval(self, approval_id: UUID) -> Approval | None:
        row = self._connection.execute(
            """
            SELECT approval_id, run_id, call_id, actor_id, tool_id, tool_version, arguments_hash,
                   target_resource, decision, decision_key, expires_at
            FROM atlas.agent_approvals WHERE approval_id = %s
            """,
            (approval_id,),
        ).fetchone()
        if row is None:
            return None
        return Approval(
            approval_id=row[0],
            run_id=row[1],
            call_id=row[2],
            actor_id=row[3],
            tool_id=row[4],
            tool_version=row[5],
            arguments_hash=row[6].strip(),
            target_resource=row[7],
            decision=row[8],
            decision_key=row[9],
            expires_at=row[10],
        )

    def save_tool_call(
        self,
        run_id: UUID,
        *,
        call_id: str,
        tool_id: str,
        tool_version: str,
        arguments_hash: str,
        status: str,
        evidence_ids: tuple[str, ...] = (),
        artifact_ids: tuple[str, ...] = (),
        error_category: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO atlas.agent_tool_calls(
              run_id, call_id, tool_id, tool_version, arguments_hash, status,
              evidence_ids, artifact_ids, error_category, started_at, completed_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id, call_id) DO UPDATE SET
              status = EXCLUDED.status, evidence_ids = EXCLUDED.evidence_ids,
              artifact_ids = EXCLUDED.artifact_ids, error_category = EXCLUDED.error_category,
              started_at = coalesce(atlas.agent_tool_calls.started_at, EXCLUDED.started_at),
              completed_at = EXCLUDED.completed_at
            """,
            (
                run_id,
                call_id,
                tool_id,
                tool_version,
                arguments_hash,
                status,
                list(evidence_ids),
                list(artifact_ids),
                error_category,
                started_at,
                completed_at,
            ),
        )
        self._connection.commit()

    def get_tool_call(self, run_id: UUID, call_id: str) -> dict[str, object] | None:
        row = self._connection.execute(
            """
            SELECT run_id, call_id, tool_id, tool_version, arguments_hash, status,
                   evidence_ids, artifact_ids, error_category, started_at, completed_at
            FROM atlas.agent_tool_calls WHERE run_id = %s AND call_id = %s
            """,
            (run_id, call_id),
        ).fetchone()
        if row is None:
            return None
        return {
            "run_id": row[0],
            "call_id": row[1],
            "tool_id": row[2],
            "tool_version": row[3],
            "arguments_hash": row[4].strip(),
            "status": row[5],
            "evidence_ids": tuple(row[6] or ()),
            "artifact_ids": tuple(row[7] or ()),
            "error_category": row[8],
            "started_at": row[9],
            "completed_at": row[10],
        }
