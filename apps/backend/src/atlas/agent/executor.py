"""Bounded tool executor with approvals, cancellation, and safe partial failure."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from time import perf_counter
from typing import cast

from atlas.agent.events import EventType, InMemoryEventStore
from atlas.agent.planning import AgentPlan, PlanValidationError
from atlas.agent.policy import Approval, PolicyError, assert_approval_matches
from atlas.agent.tools.registry import ToolCatalog

ToolHandler = Callable[[dict[str, object]], Mapping[str, object]]


def _ids(value: object) -> tuple[str, ...]:
    return tuple(str(item) for item in value) if isinstance(value, (list, tuple, set)) else ()


@dataclass(frozen=True, slots=True)
class ToolExecution:
    call_id: str
    tool_id: str
    status: str
    result: dict[str, object]
    latency_ms: float
    evidence_ids: tuple[str, ...] = ()
    artifact_ids: tuple[str, ...] = ()
    error_category: str | None = None


class BoundedExecutor:
    def __init__(self, catalog: ToolCatalog, *, events: InMemoryEventStore | None = None) -> None:
        self.catalog = catalog
        self.events = events or InMemoryEventStore()
        self.handlers: dict[str, ToolHandler] = {}

    def register(self, tool_id: str, handler: ToolHandler) -> None:
        if self.catalog.get(tool_id) is None:
            raise ValueError(f"cannot register unknown tool {tool_id}")
        self.handlers[tool_id] = handler

    @staticmethod
    def _invoke(
        handler: ToolHandler, arguments: dict[str, object], *, timeout_ms: int
    ) -> Mapping[str, object]:
        """Run a synchronous adapter behind a bounded worker boundary."""

        worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="atlas-tool")
        future = worker.submit(handler, arguments)
        try:
            return future.result(timeout=timeout_ms / 1000)
        finally:
            # A timed-out adapter cannot be force-killed safely. Cancel queued work and do not
            # block the agent run; adapters must keep their own downstream calls bounded too.
            future.cancel()
            worker.shutdown(wait=False, cancel_futures=True)

    def execute(
        self,
        plan: AgentPlan,
        *,
        actor_id: str = "anonymous",
        approvals: Mapping[str, Approval] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> tuple[ToolExecution, ...]:
        approvals = approvals or {}
        results: list[ToolExecution] = []
        self.events.emit(plan.run_id, "run.accepted", status="accepted")
        self.events.emit(plan.run_id, "plan.created", status="planned")
        completed_steps: set[str] = set()
        max_calls = plan.budget.get("max_calls", len(plan.steps))
        max_evidence = plan.budget.get("max_evidence", 64)
        used_evidence = 0
        terminal_emitted = False
        for index, step in enumerate(plan.steps):
            call_id = f"step-{index}"
            if index >= max_calls:
                self.events.emit(
                    plan.run_id,
                    "tool_call.failed",
                    status="failed",
                    tool_id=step.tool_id,
                    call_id=call_id,
                    error_category="call_budget_exceeded",
                )
                results.append(
                    ToolExecution(
                        call_id,
                        step.tool_id,
                        "failed",
                        {},
                        0,
                        error_category="call_budget_exceeded",
                    )
                )
                break
            if cancelled is not None and cancelled():
                self.events.emit(plan.run_id, "run.cancelled", status="cancelled")
                terminal_emitted = True
                results.append(ToolExecution(
                    call_id, step.tool_id, "cancelled", {}, 0, error_category="cancelled"
                ))
                break
            if not set(step.dependencies).issubset(completed_steps):
                raise PlanValidationError("tool dependencies are not completed in order")
            definition = self.catalog.get(step.tool_id)
            if definition is None or step.tool_id not in self.handlers:
                self.events.emit(
                    plan.run_id,
                    "tool_call.failed",
                    status="failed",
                    tool_id=step.tool_id,
                    call_id=call_id,
                    error_category="handler_unavailable",
                )
                results.append(ToolExecution(
                    call_id, step.tool_id, "failed", {}, 0, error_category="handler_unavailable"
                ))
                break
            if definition.approval != "none":
                approval = approvals.get(call_id)
                if approval is None:
                    self.events.emit(
                        plan.run_id,
                        "approval.requested",
                        status="awaiting_approval",
                        tool_id=step.tool_id,
                        call_id=call_id,
                    )
                    results.append(ToolExecution(
                        call_id, step.tool_id, "rejected", {}, 0,
                        error_category="approval_required",
                    ))
                    break
                try:
                    assert_approval_matches(
                        approval,
                        plan=plan,
                        actor_id=actor_id,
                        tool_id=step.tool_id,
                        tool_version=step.tool_version,
                        arguments=step.arguments,
                    )
                except PolicyError:
                    self.events.emit(
                        plan.run_id,
                        "approval.decided",
                        status="rejected",
                        tool_id=step.tool_id,
                        call_id=call_id,
                        error_category="approval_mismatch",
                    )
                    results.append(ToolExecution(
                        call_id, step.tool_id, "rejected", {}, 0,
                        error_category="approval_mismatch",
                    ))
                    break
            self.events.emit(
                plan.run_id,
                "tool_call.started",
                status="running",
                tool_id=step.tool_id,
                tool_version=step.tool_version,
                call_id=call_id,
            )
            started = perf_counter()
            try:
                raw = self._invoke(
                    self.handlers[step.tool_id],
                    dict(step.arguments),
                    timeout_ms=definition.timeout_ms,
                )
                result = dict(raw)
                status = str(result.pop("status", "completed"))
                evidence = _ids(result.pop("evidence_ids", ()))
                artifacts = _ids(result.pop("artifact_ids", ()))
                elapsed = (perf_counter() - started) * 1000
                if used_evidence + len(evidence) > max_evidence:
                    self.events.emit(
                        plan.run_id,
                        "tool_call.failed",
                        status="failed",
                        tool_id=step.tool_id,
                        call_id=call_id,
                        error_category="evidence_budget_exceeded",
                    )
                    results.append(
                        ToolExecution(
                            call_id,
                            step.tool_id,
                            "failed",
                            {},
                            elapsed,
                            error_category="evidence_budget_exceeded",
                        )
                    )
                    break
                execution = ToolExecution(
                    call_id, step.tool_id, status, result, elapsed, evidence, artifacts
                )
                results.append(execution)
                used_evidence += len(evidence)
                completed_steps.add(call_id)
                event_type = (
                    "tool_call.abstained" if status == "abstained" else "tool_call.completed"
                )
                self.events.emit(
                    plan.run_id,
                    cast(EventType, event_type),
                    status=status,
                    tool_id=step.tool_id,
                    tool_version=step.tool_version,
                    call_id=call_id,
                    evidence_ids=evidence,
                    artifact_ids=artifacts,
                )
            except TimeoutError:
                elapsed = (perf_counter() - started) * 1000
                self.events.emit(
                    plan.run_id,
                    "tool_call.failed",
                    status="failed",
                    tool_id=step.tool_id,
                    call_id=call_id,
                    error_category="timeout",
                )
                results.append(
                    ToolExecution(
                        call_id,
                        step.tool_id,
                        "failed",
                        {},
                        elapsed,
                        error_category="timeout",
                    )
                )
                break
            except Exception as exc:
                elapsed = (perf_counter() - started) * 1000
                self.events.emit(
                    plan.run_id,
                    "tool_call.failed",
                    status="failed",
                    tool_id=step.tool_id,
                    call_id=call_id,
                    error_category=type(exc).__name__,
                )
                results.append(
                    ToolExecution(
                        call_id,
                        step.tool_id,
                        "failed",
                        {},
                        elapsed,
                        error_category=type(exc).__name__,
                    )
                )
                break
        final_status = (
            "completed"
            if results and results[-1].status == "completed"
            else results[-1].status
            if results
            else "failed"
        )
        if not terminal_emitted:
            self.events.emit(
                plan.run_id,
                "run.completed" if final_status == "completed" else "run.failed",
                status=final_status,
            )
        return tuple(results)
