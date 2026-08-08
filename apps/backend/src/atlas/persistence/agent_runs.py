"""In-memory durable-port substitute for agent plans, calls, and ordered events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from atlas.agent.events import AgentRunEvent, InMemoryEventStore
from atlas.agent.planning import AgentPlan


@dataclass(frozen=True, slots=True)
class AgentRunRecord:
    run_id: UUID
    request: str
    locale: str
    plan_hash: str
    status: str
    created_at: datetime
    output: dict[str, object]


class InMemoryAgentRunRepository:
    def __init__(self, *, events: InMemoryEventStore | None = None) -> None:
        self.events = events or InMemoryEventStore()
        self._runs: dict[UUID, AgentRunRecord] = {}
        self._plans: dict[str, AgentPlan] = {}

    def save_plan(self, plan: AgentPlan) -> AgentPlan:
        self._plans[plan.plan_hash] = plan
        return plan

    def get_plan(self, plan_hash: str) -> AgentPlan | None:
        return self._plans.get(plan_hash)

    def create_run(self, plan: AgentPlan) -> AgentRunRecord:
        record = AgentRunRecord(
            plan.run_id,
            plan.request,
            plan.locale,
            plan.plan_hash,
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
