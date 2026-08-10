"""Safe API boundary for deterministic planning and human review decisions."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime
from time import perf_counter
from typing import Annotated, Literal, cast
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from atlas.agent.checkpoints import CheckpointRepository
from atlas.agent.orchestration import AgentOrchestrator
from atlas.agent.planner import AgentPlanner
from atlas.agent.planning import AgentPlan, PlanValidationError, arguments_hash, validate_plan
from atlas.agent.policy import Approval, PolicyError, assert_approval_matches, issue_approval
from atlas.agent.review import ReviewService
from atlas.agent.state import AtlasState
from atlas.agent.tools.read_only import ReadOnlyToolAdapters, bounded_result, is_read_only_tool
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import Locale, ToolCallRequest, validate_json_object
from atlas.agent.tools.side_effects import (
    SIDE_EFFECT_TOOL_IDS,
    SideEffectToolAdapters,
    abstained_result,
)
from atlas.api.routes.answers import AnswerRunControl
from atlas.api.routes.comparisons import ComparisonRunControl
from atlas.observability.agent_trace import agent_trace_fields, agent_trace_tags
from atlas.observability.context import current_request_id
from atlas.observability.langsmith import TraceHandle, TraceSink
from atlas.persistence.agent_runs import (
    AgentIdempotencyStore,
    AgentRunRepository,
    IdempotencyConflict,
)
from atlas.reports.schemas import ReportFormat, ReportLocale, ReportSpec

router = APIRouter(prefix="/v1/agent", tags=["Agent orchestration"])


def _tool_catalog(request: Request) -> ToolCatalog:
    return cast(ToolCatalog, request.app.state.agent_tool_catalog)


def _planner(request: Request) -> AgentPlanner:
    return cast(AgentPlanner, request.app.state.agent_planner)


def _runs(request: Request) -> AgentRunRepository:
    return cast(AgentRunRepository, request.app.state.agent_run_repository)


def _idempotency_store(request: Request) -> AgentIdempotencyStore:
    return cast(AgentIdempotencyStore, request.app.state.agent_idempotency)


def _idempotency_scope(request: Request, operation: str) -> str:
    if not getattr(request.app.state.agent_idempotency, "owner_scoped", False):
        return operation
    owner = hashlib.sha256(_visitor_hash(request).encode()).hexdigest()[:16]
    return f"{operation}:{owner}"


def _normalize_idempotency_key(key: str | None) -> str | None:
    if key is None:
        return None
    normalized = key.strip()
    if not 8 <= len(normalized) <= 128:
        raise HTTPException(status_code=400, detail="Idempotency-Key must be 8-128 characters")
    return normalized


def _fingerprint(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@router.get("/tools")
def list_tools(request: Request, locale: Locale = "en-US") -> dict[str, object]:
    """Return the safe, localized allowlist used by the planner and agent workspace."""

    catalog = _tool_catalog(request)
    tools = []
    for tool in catalog.list_for_locale(locale):
        item = tool.model_dump(mode="json")
        localized = item["localization"][locale]
        item["name"] = localized["name"]
        item["description"] = localized["description"]
        tools.append(item)
    return {
        "version": catalog.version,
        "locale": locale,
        "tools": tools,
    }


class PlanCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: str = Field(min_length=1, max_length=4000)
    locale: Locale = "en-US"
    selected_tool: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_]{2,63}$")
    input: dict[str, object] = Field(default_factory=dict)
    actor_id: str = Field(default="anonymous", min_length=1, max_length=128)


class RunCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    actor_id: str = Field(default="anonymous", min_length=1, max_length=128)
    approval_ids: list[str] = Field(default_factory=list, max_length=8)


class ApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_id: str = Field(min_length=1, max_length=128)
    decision: Literal["approved", "rejected"]
    decision_key: str = Field(min_length=1, max_length=128)


def _visitor_hash(request: Request) -> str:
    return getattr(request.state, "visitor_key_hash", "development-anonymous-visitor")


def _request_actor(request: Request, actor_id: str | None) -> str:
    """Resolve the caller identity used for durable run ownership checks."""

    return (actor_id or request.headers.get("x-atlas-actor-id") or "anonymous").strip()


def _assert_run_actor(request: Request, record: object, actor_id: str | None) -> None:
    resolved_actor = _request_actor(request, actor_id)
    if getattr(record, "actor_id", "anonymous") != resolved_actor:
        raise HTTPException(status_code=404, detail="run not found")


def _result_ids(value: object) -> tuple[str, ...]:
    if isinstance(value, (list, tuple, set)):
        return tuple(str(item) for item in value)
    return ()


@router.post("/plans")
async def create_plan(
    payload: PlanCreateRequest,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = _normalize_idempotency_key(idempotency_key)
    fingerprint = _fingerprint(payload.model_dump(mode="json"))
    if key is not None:
        try:
            cached = _idempotency_store(request).get(
                _idempotency_scope(request, "agent.plan"), key, fingerprint
            )
        except IdempotencyConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if cached is not None:
            return cached
    catalog = _tool_catalog(request)
    try:
        if payload.selected_tool is None:
            plan = await _planner(request).propose_async(payload.request, locale=payload.locale)
        else:
            definition = catalog.get(payload.selected_tool)
            if definition is None:
                raise PlanValidationError(f"unknown tool: {payload.selected_tool}")
            arguments = validate_json_object(payload.input, definition.input_schema)
            plan = validate_plan(
                catalog=catalog,
                request=payload.request,
                locale=payload.locale,
                steps=(
                    ToolCallRequest(
                        tool_id=definition.tool_id,
                        tool_version=definition.version,
                        arguments=arguments,
                    ),
                ),
            )
    except (PlanValidationError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _runs(request).save_plan(plan)
    approvals = cast(dict[str, Approval], request.app.state.agent_approvals)
    approval_ids: list[str] = []
    approval_keys: dict[str, str] = {}
    for index, step in enumerate(plan.steps):
        definition = catalog.get(step.tool_id)
        if definition is not None and definition.approval != "none":
            approval = issue_approval(
                plan,
                call_id=f"step-{index}",
                actor_id=payload.actor_id,
                tool_id=step.tool_id,
                tool_version=step.tool_version,
                arguments=step.arguments,
            )
            approvals[approval.call_id] = approval
            approval_ids.append(str(approval.approval_id))
            approval_keys[str(approval.approval_id)] = approval.decision_key
    response = {
        **plan.model_dump(mode="json"),
        "required_approval_ids": approval_ids,
        "approval_decision_keys": approval_keys,
    }
    if key is not None:
        _idempotency_store(request).save(
            _idempotency_scope(request, "agent.plan"), key, fingerprint, response
        )
    return response


async def _execute_domain_tool(
    request: Request,
    plan: AgentPlan,
    step_index: int,
    *,
    actor_id: str,
    approval: Approval | None,
) -> dict[str, object]:
    """Route read-only calls through the typed adapter boundary before domain services."""

    step = plan.steps[step_index]
    if not is_read_only_tool(step.tool_id):
        if step.tool_id in SIDE_EFFECT_TOOL_IDS:
            async def side_effect_delegate(_arguments: dict[str, object]) -> dict[str, object]:
                return await _execute_domain_tool_legacy(request, plan, step_index)

            def owner_check(candidate_actor: str, arguments: Mapping[str, object]) -> bool:
                service = request.app.state.private_resource_service
                if service is None:
                    return False
                try:
                    owner_id = UUID(candidate_actor)
                    resource_id = UUID(str(arguments["resource_id"]))
                    service.get_owned(owner_id, resource_id)
                except (KeyError, TypeError, ValueError):
                    return False
                return True

            adapters = SideEffectToolAdapters(
                _tool_catalog(request),
                {step.tool_id: side_effect_delegate},
                owner_check=owner_check,
            )
            return await adapters.execute(
                step.tool_id,
                step.arguments,
                plan=plan,
                actor_id=actor_id,
                approval=approval,
            )
        return await _execute_domain_tool_legacy(request, plan, step_index)

    async def read_only_delegate(_arguments: dict[str, object]) -> dict[str, object]:
        return await _execute_domain_tool_legacy(request, plan, step_index)

    read_only_adapters = ReadOnlyToolAdapters({step.tool_id: read_only_delegate})
    return await read_only_adapters.execute(step.tool_id, step.arguments)


async def _execute_domain_tool_legacy(
    request: Request, plan: AgentPlan, step_index: int
) -> dict[str, object]:
    """Delegate read-only tools to the existing domain services and preserve their IDs."""

    step = plan.steps[step_index]
    request_id = current_request_id() or plan.run_id
    idempotency_key = f"agent-{plan.run_id}-{step_index}"
    if step.tool_id == "cited_answer":
        service = cast(AnswerRunControl | None, request.app.state.answer_service)
        if service is None:
            return bounded_result(status="abstained", reason="answer_service_unavailable")
        run_id = await service.start(
            question={
                "question": step.arguments.get("question", plan.request),
                "language": plan.locale,
            },
            visitor_key_hash=_visitor_hash(request),
            idempotency_key=idempotency_key,
            request_id=request_id,
        )
        return {"status": "queued", "artifact_ids": (f"answer_run:{run_id}",)}
    if step.tool_id == "comparison":
        comparison_service = cast(
            ComparisonRunControl | None, request.app.state.comparison_service
        )
        if comparison_service is None:
            return bounded_result(status="abstained", reason="comparison_service_unavailable")
        run_id = await comparison_service.start(
            comparison=step.arguments,
            visitor_key_hash=_visitor_hash(request),
            idempotency_key=idempotency_key,
            request_id=request_id,
        )
        return {"status": "queued", "artifact_ids": (f"comparison_run:{run_id}",)}
    if step.tool_id == "report":
        service = request.app.state.report_service
        if service is None:
            return bounded_result(status="abstained", reason="report_service_unavailable")
        spec = ReportSpec(
            source_run_id=UUID(str(step.arguments["source_run_id"])),
            audience=str(step.arguments.get("audience", "technical reviewer")),
            scope=str(step.arguments.get("scope", plan.request)),
            locale=ReportLocale(plan.locale),
            format=ReportFormat(str(step.arguments.get("format", "pdf"))),
        )
        report_id = await service.create(
            spec,
            owner_key_hash=_visitor_hash(request),
            idempotency_key=idempotency_key,
            request_id=request_id,
        )
        return {"status": "queued", "artifact_ids": (f"report:{report_id}",)}
    if step.tool_id == "daily_news":
        service = request.app.state.news_service
        if service is None:
            return bounded_result(status="abstained", reason="news_unavailable")
        selection = service.get_daily()
        candidate = selection.candidate
        evidence = (str(candidate.id),) if candidate is not None else ()
        return bounded_result(status=selection.status, evidence_ids=evidence)
    if step.tool_id == "corpus_status":
        service = request.app.state.corpus_service
        if service is None:
            return bounded_result(status="abstained", reason="corpus_unavailable")
        status_value = service.get_status()
        return bounded_result(status="completed" if status_value is not None else "abstained")
    return abstained_result(step.tool_id)


@router.post("/runs", status_code=202)
async def create_agent_run(
    payload: RunCreateRequest,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = _normalize_idempotency_key(idempotency_key)
    fingerprint = _fingerprint(payload.model_dump(mode="json"))
    if key is not None:
        try:
            cached = _idempotency_store(request).get(
                _idempotency_scope(request, "agent.run"), key, fingerprint
            )
        except IdempotencyConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if cached is not None:
            return cached
    repository = _runs(request)
    plan = repository.get_plan(payload.plan_hash)
    if plan is None:
        raise HTTPException(status_code=404, detail="plan not found")
    if plan.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=409, detail="plan expired")
    trace_sink = cast(TraceSink | None, getattr(request.app.state, "agent_trace_sink", None))
    trace_handle: TraceHandle | None = None
    trace_started = perf_counter()
    if trace_sink is not None:
        trace_handle = trace_sink.start(
            "agent.run",
            request_id=current_request_id() or plan.run_id,
            run_id=plan.run_id,
            fields=agent_trace_fields(plan),
            tags=agent_trace_tags(plan),
        )
    approvals = cast(dict[str, Approval], request.app.state.agent_approvals)
    repository.create_run(plan, actor_id=payload.actor_id)
    for stored_approval in approvals.values():
        if stored_approval.run_id == plan.run_id:
            repository.save_approval(stored_approval)
    repository.events.emit(plan.run_id, "run.accepted", status="accepted")
    repository.events.emit(plan.run_id, "plan.created", status="planned")
    for index, step in enumerate(plan.steps):
        definition = _tool_catalog(request).get(step.tool_id)
        call_id = f"step-{index}"
        if definition is None:
            raise HTTPException(status_code=400, detail="unknown tool")
        approval_for_execution: Approval | None = None
        if definition.approval != "none":
            approval: Approval | None = approvals.get(call_id)
            if approval is None:
                for approval_id in payload.approval_ids:
                    try:
                        candidate = repository.get_approval(UUID(approval_id))
                    except ValueError:
                        candidate = None
                    if candidate is not None and candidate.call_id == call_id:
                        approval = candidate
                        break
            if approval is None or str(approval.approval_id) not in payload.approval_ids:
                repository.save_tool_call(
                    plan.run_id,
                    call_id=call_id,
                    tool_id=step.tool_id,
                    tool_version=step.tool_version,
                    arguments_hash=arguments_hash(step.arguments),
                    status="awaiting_approval",
                )
                repository.events.emit(
                    plan.run_id,
                    "approval.requested",
                    status="awaiting_approval",
                    tool_id=step.tool_id,
                    call_id=call_id,
                )
                repository.update(plan.run_id, status="awaiting_approval")
                if trace_handle is not None and trace_sink is not None:
                    trace_sink.end(
                        trace_handle,
                        status="awaiting_approval",
                        fields={"latency_ms": (perf_counter() - trace_started) * 1000},
                    )
                pending_response: dict[str, object] = {
                    "run_id": str(plan.run_id),
                    "status": "awaiting_approval",
                    "events": [
                        event.model_dump(mode="json")
                        for event in repository.list_events(plan.run_id)
                    ],
                }
                if key is not None:
                    _idempotency_store(request).save(
                        _idempotency_scope(request, "agent.run"), key, fingerprint, pending_response
                    )
                return pending_response
            approval_for_execution = approval
            try:
                assert_approval_matches(
                    approval,
                    plan=plan,
                    actor_id=payload.actor_id,
                    tool_id=step.tool_id,
                    tool_version=step.tool_version,
                    arguments=step.arguments,
                )
            except PolicyError as exc:
                repository.save_tool_call(
                    plan.run_id,
                    call_id=call_id,
                    tool_id=step.tool_id,
                    tool_version=step.tool_version,
                    arguments_hash=arguments_hash(step.arguments),
                    status="rejected",
                    error_category="approval_mismatch",
                    completed_at=datetime.now(UTC),
                )
                repository.events.emit(
                    plan.run_id,
                    "approval.decided",
                    status="rejected",
                    tool_id=step.tool_id,
                    call_id=call_id,
                    error_category="approval_mismatch",
                )
                repository.update(plan.run_id, status="rejected")
                if trace_handle is not None and trace_sink is not None:
                    trace_sink.end(
                        trace_handle,
                        status="rejected",
                        fields={"latency_ms": (perf_counter() - trace_started) * 1000},
                    )
                raise HTTPException(status_code=403, detail=str(exc)) from exc
        started_at = datetime.now(UTC)
        repository.save_tool_call(
            plan.run_id,
            call_id=call_id,
            tool_id=step.tool_id,
            tool_version=step.tool_version,
            arguments_hash=arguments_hash(step.arguments),
            status="running",
            started_at=started_at,
        )
        result = await _execute_domain_tool(
            request,
            plan,
            index,
            actor_id=payload.actor_id,
            approval=approval_for_execution,
        )
        status_value = str(result.get("status", "completed"))
        repository.save_tool_call(
            plan.run_id,
            call_id=call_id,
            tool_id=step.tool_id,
            tool_version=step.tool_version,
            arguments_hash=arguments_hash(step.arguments),
            status=status_value,
            evidence_ids=_result_ids(result.get("evidence_ids", ())),
            artifact_ids=_result_ids(result.get("artifact_ids", ())),
            error_category=str(result["reason"]) if result.get("reason") else None,
            started_at=started_at,
            completed_at=datetime.now(UTC),
        )
        event_type = (
            "tool_call.abstained"
            if status_value == "abstained"
            else "tool_call.failed"
            if status_value in {"failed", "rejected"}
            else "tool_call.completed"
        )
        repository.events.emit(
            plan.run_id,
            event_type,
            status=status_value,
            tool_id=step.tool_id,
            call_id=call_id,
            evidence_ids=_result_ids(result.get("evidence_ids", ())),
            artifact_ids=_result_ids(result.get("artifact_ids", ())),
        )
    repository.events.emit(plan.run_id, "run.completed", status="completed")
    repository.update(
        plan.run_id,
        status="completed",
        output={"event_count": len(repository.list_events(plan.run_id))},
    )
    if trace_handle is not None and trace_sink is not None:
        trace_sink.end(
            trace_handle,
            status="completed",
            fields={
                "event_count": len(repository.list_events(plan.run_id)),
                "latency_ms": (perf_counter() - trace_started) * 1000,
            },
        )
    completed_response: dict[str, object] = {
        "run_id": str(plan.run_id),
        "status": "completed",
        "events": [event.model_dump(mode="json") for event in repository.list_events(plan.run_id)],
    }
    if key is not None:
        _idempotency_store(request).save(
            _idempotency_scope(request, "agent.run"), key, fingerprint, completed_response
        )
    return completed_response


@router.get("/runs/{run_id}")
def get_agent_run(
    run_id: UUID, request: Request, actor_id: str | None = None
) -> dict[str, object]:
    record = _runs(request).get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    _assert_run_actor(request, record, actor_id)
    return {
        "run_id": str(run_id),
        "status": record.status,
        "plan_hash": record.plan_hash,
        "output": record.output,
    }


@router.get("/runs/{run_id}/events")
def get_agent_events(
    run_id: UUID,
    request: Request,
    after_sequence: int = 0,
    actor_id: str | None = None,
) -> dict[str, object]:
    record = _runs(request).get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    _assert_run_actor(request, record, actor_id)
    return {
        "run_id": str(run_id),
        "events": [
            event.model_dump(mode="json")
            for event in _runs(request).list_events(run_id, after_sequence)
        ],
    }


@router.post("/runs/{run_id}/cancel")
def cancel_agent_run(
    run_id: UUID, request: Request, actor_id: str | None = None
) -> dict[str, object]:
    """Cancel a queued or approval-blocked run without executing another tool."""

    repository = _runs(request)
    record = repository.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    _assert_run_actor(request, record, actor_id)
    if record.status in {"completed", "failed", "rejected", "cancelled"}:
        raise HTTPException(status_code=409, detail="run is no longer cancellable")
    repository.events.emit(run_id, "run.cancelled", status="cancelled")
    repository.update(run_id, status="cancelled")
    return {"run_id": str(run_id), "status": "cancelled"}


@router.post("/runs/{run_id}/resume")
def resume_agent_run(
    run_id: UUID, request: Request, actor_id: str | None = None
) -> dict[str, object]:
    """Resume only from a known run record; tools are never replayed implicitly."""

    repository = _runs(request)
    record = repository.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    _assert_run_actor(request, record, actor_id)
    if record.status not in {"cancelled", "awaiting_approval"}:
        raise HTTPException(status_code=409, detail="run is not resumable")
    repository.events.emit(run_id, "run.resumed", status="resumed")
    repository.update(run_id, status="accepted")
    return {"run_id": str(run_id), "status": "accepted"}


@router.post("/approvals/{approval_id}/decision")
def decide_agent_approval(
    approval_id: UUID,
    payload: ApprovalDecisionRequest,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> dict[str, object]:
    key = _normalize_idempotency_key(idempotency_key)
    fingerprint = _fingerprint({"approval_id": str(approval_id), **payload.model_dump(mode="json")})
    if key is not None:
        try:
            cached = _idempotency_store(request).get(
                _idempotency_scope(request, "agent.approval"), key, fingerprint
            )
        except IdempotencyConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if cached is not None:
            return cached
    pending = cast(dict[str, Approval], request.app.state.agent_approvals)
    approval = next((item for item in pending.values() if item.approval_id == approval_id), None)
    if approval is None:
        approval = _runs(request).get_approval(approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="approval not found")
    if approval.actor_id != payload.actor_id or approval.decision_key != payload.decision_key:
        raise HTTPException(status_code=403, detail="approval decision mismatch")
    if payload.decision == "rejected":
        updated_approval = replace(approval, decision="rejected")
        pending[approval.call_id] = updated_approval
        response: dict[str, object] = {
            "approval_id": str(approval_id),
            "decision": "rejected",
        }
    else:
        updated_approval = replace(approval, decision="approved")
        pending[approval.call_id] = updated_approval
        response = {
            "approval_id": str(approval_id),
            "decision": "approved",
        }
    if _runs(request).get(updated_approval.run_id) is not None:
        _runs(request).save_approval(updated_approval)
    if key is not None:
        _idempotency_store(request).save(
            _idempotency_scope(request, "agent.approval"), key, fingerprint, response
        )
    return response


class PrepareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: str = Field(min_length=1, max_length=4000)
    language: str = "en-US"
    thread_id: UUID | None = None


class ReviewCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: UUID
    evidence_ids: list[str] = Field(min_length=1, max_length=64)
    proposed_text: str = Field(min_length=1, max_length=20_000)
    reviewer_id: str = Field(min_length=1, max_length=128)


class ReviewDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer_id: str = Field(min_length=1, max_length=128)
    action: Literal["approve", "edit", "reject"]
    decision_key: str = Field(min_length=1, max_length=128)
    edited_text: str | None = Field(default=None, max_length=20_000)


def _review(request: Request) -> ReviewService:
    return cast(ReviewService, request.app.state.agent_review_service)


def _checkpoints(request: Request) -> CheckpointRepository:
    return cast(CheckpointRepository, request.app.state.agent_checkpoint_service)


@router.post("/prepare")
def prepare(payload: PrepareRequest, request: Request) -> dict[str, object]:
    orchestrator = cast(AgentOrchestrator, request.app.state.agent_orchestrator)
    if payload.thread_id is None:
        state = orchestrator.run(AtlasState(request=payload.request, language=payload.language))
    else:
        state = orchestrator.run(
            AtlasState(
                request=payload.request,
                language=payload.language,
                thread_id=payload.thread_id,
            )
        )
    checkpoint = _checkpoints(request).save(state, node="plan", replay_key=str(state.request_id))
    return {
        "thread_id": str(state.thread_id),
        "request_id": str(state.request_id),
        "checkpoint_id": str(checkpoint.checkpoint_id),
        "route": state.route.model_dump(mode="json"),
        "node_history": state.node_history,
        "node_events": [event.model_dump(mode="json") for event in state.node_events],
        "errors": state.errors,
    }


@router.get("/threads/{thread_id}/status")
def thread_status(thread_id: UUID, request: Request, replay_key: str) -> dict[str, object]:
    checkpoint = _checkpoints(request).resume(thread_id, replay_key=replay_key)
    return {
        "thread_id": str(thread_id),
        "checkpoint_id": str(checkpoint.checkpoint_id),
        "node": checkpoint.node,
        "safe_summary": checkpoint.safe_summary,
    }


@router.post("/threads/{thread_id}/resume")
def resume_thread(thread_id: UUID, request: Request, replay_key: str) -> dict[str, object]:
    claimed = _checkpoints(request).claim_resume(thread_id, replay_key=replay_key)
    checkpoint = _checkpoints(request).resume(thread_id, replay_key=replay_key)
    return {
        "thread_id": str(thread_id),
        "checkpoint_id": str(checkpoint.checkpoint_id),
        "claimed": claimed,
        "node": checkpoint.node,
    }


@router.post("/reviews")
def create_review(payload: ReviewCreateRequest, request: Request) -> dict[str, object]:
    review = _review(request).create(**payload.model_dump())
    return {
        "id": str(review.id),
        "status": review.status.value,
        "expires_at": review.expires_at.isoformat(),
    }


@router.post("/reviews/{review_id}/decision")
def decide_review(
    review_id: UUID, payload: ReviewDecisionRequest, request: Request
) -> dict[str, object]:
    review = _review(request).decide(review_id, **payload.model_dump())
    return {
        "id": str(review.id),
        "status": review.status.value,
        "decision_key": review.decision_key,
    }
