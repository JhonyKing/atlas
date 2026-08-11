from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.demo import DemoCorpusStatusProvider
from atlas.news.feeds import parse_feed
from atlas.news.ranking import InMemoryDailyNewsService
from atlas.observability.langsmith import TraceHandle


class RecordingTraceSink:
    def __init__(self) -> None:
        self.started: list[tuple[str, dict[str, object]]] = []
        self.finished: list[tuple[str, str, dict[str, object]]] = []

    def start(self, name: str, **kwargs: object) -> TraceHandle:
        self.started.append((name, dict(kwargs)))
        run_id = kwargs["run_id"]
        assert isinstance(run_id, UUID)
        return TraceHandle(run_id=run_id, active=True)

    def end(self, handle: TraceHandle, *, status: str, fields: object = None) -> None:
        safe_fields = fields if isinstance(fields, dict) else {}
        self.finished.append((str(handle.run_id), status, safe_fields))


def test_cancel_and_resume_emit_content_free_lifecycle_traces() -> None:
    sink = RecordingTraceSink()
    client = TestClient(create_app(news_trace_sink=sink))
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "Delete my private resource",
            "selected_tool": "private_delete",
            "input": {"resource_id": "resource-trace"},
        },
    ).json()
    run = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]}).json()
    run_id = run["run_id"]

    assert client.post(f"/v1/agent/runs/{run_id}/cancel").json()["status"] == "cancelled"
    assert client.post(f"/v1/agent/runs/{run_id}/resume").json()["status"] == "accepted"

    lifecycle = [name for name, _ in sink.started if name.startswith("agent.run.")]
    assert lifecycle == ["agent.run.cancel", "agent.run.resume"]
    assert [status for _, status, _ in sink.finished[-2:]] == ["cancelled", "resumed"]
    for _, _, fields in sink.finished[-2:]:
        assert isinstance(fields["run_id"], str)
        assert isinstance(fields["latency_ms"], float)
        assert fields["tokens"] == "not_reported"
        assert fields["cost_usd"] == "not_reported"


def test_tool_catalog_and_read_only_run_are_explicit() -> None:
    client = TestClient(create_app())
    catalog = client.get("/v1/agent/tools", params={"locale": "es-MX"})
    assert catalog.status_code == 200
    assert catalog.json()["locale"] == "es-MX"
    assert {tool["tool_id"] for tool in catalog.json()["tools"]} >= {
        "cited_answer",
        "private_delete",
    }

    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "How does LangGraph persist state?",
            "locale": "en-US",
            "selected_tool": "cited_answer",
            "input": {"question": "How does LangGraph persist state?"},
        },
    )
    assert plan.status_code == 200
    assert plan.json()["required_approval_ids"] == []
    run = client.post("/v1/agent/runs", json={"plan_hash": plan.json()["plan_hash"]})
    assert run.status_code == 202
    assert run.json()["status"] == "completed"
    assert run.json()["output"]["tool_results"][0]["status"] == "abstained"
    assert [event["event_type"] for event in run.json()["events"]] == [
        "run.accepted",
        "plan.created",
        "tool_call.abstained",
        "run.completed",
    ]
    tool_call = client.app.state.agent_run_repository.get_tool_call(
        UUID(run.json()["run_id"]), "step-0"
    )
    assert tool_call is not None
    assert tool_call["status"] == "abstained"


def test_side_effect_tool_stays_blocked_until_explicit_approval() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "Delete my private resource",
            "locale": "en-US",
            "selected_tool": "private_delete",
            "input": {"resource_id": "resource-1"},
        },
    )
    assert plan.status_code == 200
    body = plan.json()
    approval_id = body["required_approval_ids"][0]
    pending = client.post("/v1/agent/runs", json={"plan_hash": body["plan_hash"]})
    assert pending.status_code == 202
    assert pending.json()["status"] == "awaiting_approval"
    pending_call = client.app.state.agent_run_repository.get_tool_call(
        UUID(pending.json()["run_id"]), "step-0"
    )
    assert pending_call is not None
    assert pending_call["status"] == "awaiting_approval"

    decision = client.post(
        f"/v1/agent/approvals/{approval_id}/decision",
        json={
            "actor_id": "anonymous",
            "decision": "approved",
            "decision_key": body["approval_decision_keys"][approval_id],
        },
    )
    assert decision.status_code == 200
    completed = client.post(
        "/v1/agent/runs",
        json={"plan_hash": body["plan_hash"], "approval_ids": [approval_id]},
    )
    assert completed.status_code == 202
    assert completed.json()["status"] == "completed"
    assert any(event["event_type"] == "tool_call.failed" for event in completed.json()["events"])
    completed_call = client.app.state.agent_run_repository.get_tool_call(
        UUID(completed.json()["run_id"]), "step-0"
    )
    assert completed_call is not None
    assert completed_call["status"] == "rejected"


def test_run_cancel_and_resume_are_explicit_and_non_replaying() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "What is the corpus status?",
            "locale": "en-US",
            "selected_tool": "corpus_status",
            "input": {},
        },
    ).json()
    run = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]}).json()
    run_id = run["run_id"]
    cancelled = client.post(f"/v1/agent/runs/{run_id}/cancel")
    assert cancelled.status_code == 409

    private_plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "Delete my private resource",
            "locale": "en-US",
            "selected_tool": "private_delete",
            "input": {"resource_id": "resource-2"},
        },
    ).json()
    pending = client.post(
        "/v1/agent/runs", json={"plan_hash": private_plan["plan_hash"]}
    ).json()
    pending_id = pending["run_id"]
    assert client.post(f"/v1/agent/runs/{pending_id}/cancel").json()["status"] == "cancelled"
    resumed = client.post(f"/v1/agent/runs/{pending_id}/resume")
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "accepted"


def test_explicit_resume_execution_reuses_the_durable_run_boundary() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "Delete my private resource",
            "selected_tool": "private_delete",
            "input": {"resource_id": "resource-2"},
        },
    ).json()
    approval_id = plan["required_approval_ids"][0]
    pending = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]}).json()
    run_id = pending["run_id"]
    assert client.post(f"/v1/agent/runs/{run_id}/cancel").json()["status"] == "cancelled"
    decision = client.post(
        f"/v1/agent/approvals/{approval_id}/decision",
        json={
            "actor_id": "anonymous",
            "decision": "approved",
            "decision_key": plan["approval_decision_keys"][approval_id],
        },
    )
    assert decision.status_code == 200

    resumed = client.post(
        f"/v1/agent/runs/{run_id}/resume",
        params={"execute": "true", "approval_ids": approval_id, "consent": "true"},
    )
    assert resumed.status_code == 200
    assert any(event["event_type"] == "run.resumed" for event in resumed.json()["events"])


def test_durable_run_reads_require_the_persisted_actor() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "What is the corpus status?",
            "selected_tool": "corpus_status",
            "input": {},
            "actor_id": "user-42",
        },
    ).json()
    run = client.post(
        "/v1/agent/runs",
        json={"plan_hash": plan["plan_hash"], "actor_id": "user-42"},
    ).json()
    run_id = run["run_id"]

    assert client.get(f"/v1/agent/runs/{run_id}").status_code == 404
    assert client.get(
        f"/v1/agent/runs/{run_id}", params={"actor_id": "user-42"}
    ).status_code == 200


def test_replaying_completed_run_does_not_duplicate_events_or_tool_calls() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "What is the corpus status?",
            "selected_tool": "corpus_status",
            "input": {},
        },
    ).json()
    first = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]})
    second = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]})

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["output"] == first.json()["output"]
    assert second.json()["events"] == first.json()["events"]

    checkpoint = client.app.state.agent_checkpoint_service.resume(
        UUID(first.json()["run_id"]),
        replay_key=f"agent-run:{plan['plan_hash']}:step-0",
    )
    assert checkpoint.node == "tool_call:step-0"


def test_replaying_run_with_a_different_actor_is_not_allowed() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "What is the corpus status?",
            "selected_tool": "corpus_status",
            "input": {},
            "actor_id": "user-42",
        },
    ).json()
    first = client.post(
        "/v1/agent/runs",
        json={"plan_hash": plan["plan_hash"], "actor_id": "user-42"},
    )
    replay = client.post(
        "/v1/agent/runs",
        json={"plan_hash": plan["plan_hash"], "actor_id": "user-99"},
    )

    assert first.status_code == 202
    assert replay.status_code == 404


def test_daily_news_agent_tool_preserves_stable_evidence_metadata() -> None:
    observed = datetime.now(UTC)
    published_at = observed.replace(hour=12, minute=0, second=0, microsecond=0) - timedelta(days=1)
    candidates = parse_feed(
        f"""<rss><channel><item><title>Internet signal</title>
        <link>https://news.example/story</link>
        <pubDate>{format_datetime(published_at, usegmt=True)}</pubDate>
        <description>Bounded summary</description></item></channel></rss>""".encode(),
        publisher="Example News",
        captured_at=observed,
        authority_score=0.9,
        topic_score=0.9,
    )
    client = TestClient(
        create_app(news_service=InMemoryDailyNewsService(candidates))
    )
    plan = client.post(
        "/v1/agent/plans",
        json={"request": "Show the previous day's news", "selected_tool": "daily_news"},
    ).json()

    run = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]})

    assert run.status_code == 202
    assert run.json()["status"] == "completed"
    event = run.json()["events"][2]
    assert event["event_type"] == "tool_call.completed"
    assert event["evidence_ids"] == [f"news:{candidates[0].content_sha256}"]
    tool_result = run.json()["output"]["tool_results"][0]
    assert tool_result["provenance"]["publisher"] == "Example News"
    assert tool_result["excerpts"][0]["evidence_id"] == event["evidence_ids"][0]
    assert tool_result["excerpts"][0]["canonical_url"] == "https://news.example/story"


def test_corpus_status_agent_tool_preserves_snapshot_provenance_and_link() -> None:
    client = TestClient(create_app(corpus_service=DemoCorpusStatusProvider()))
    plan = client.post(
        "/v1/agent/plans",
        json={"request": "Inspect corpus status", "selected_tool": "corpus_status"},
    ).json()

    run = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]})

    assert run.status_code == 202
    tool_result = run.json()["output"]["tool_results"][0]
    assert tool_result["artifact_links"] == {"corpus_status": "/v1/corpus"}
    assert tool_result["provenance"]["snapshot_id"]
    assert tool_result["provenance"]["generated_at"]
