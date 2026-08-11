"""Run content-free representative agent journeys and export live trace evidence.

The command is intentionally opt-in: it uses the configured LangSmith sink and a local
``create_app`` instance, but stores only opaque run/trace identifiers, bounded lifecycle states,
and latency fields. It never writes questions, arguments, excerpts, or private resource data to
the evidence artifact.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.config import get_settings
from atlas.news.feeds import parse_feed
from atlas.news.ranking import InMemoryDailyNewsService
from atlas.observability.langsmith import TraceHandle, TraceSink


class RecordingTraceSink:
    """Capture only trace handles and safe terminal metadata around a real sink."""

    def __init__(self, delegate: TraceSink) -> None:
        self.delegate = delegate
        self.records: list[dict[str, object]] = []

    def start(self, name: str, **kwargs: Any) -> TraceHandle:
        handle = self.delegate.start(name, **kwargs)
        fields = kwargs.get("fields")
        source_fields = fields if isinstance(fields, dict) else {}
        safe_start_fields = {
            key: source_fields[key]
            for key in (
                "run_id",
                "plan_hash",
                "model",
                "locale",
                "corpus",
                "tokens",
                "cost_usd",
                "latency_ms",
                "budget_usd",
                "approval_required",
            )
            if key in source_fields
        }
        self.records.append(
            {
                "trace_id": str(handle.run_id),
                "operation": name,
                "active": handle.active,
                "status": "started",
                "fields": safe_start_fields,
            }
        )
        return handle

    def end(self, handle: TraceHandle, *, status: str, fields: Any = None) -> None:
        safe_fields = fields if isinstance(fields, dict) else {}
        safe = {
            key: safe_fields[key]
            for key in ("latency_ms", "tokens", "cost_usd", "outcome")
            if key in safe_fields
        }
        self.delegate.end(handle, status=status, fields=safe)
        self.records.append(
            {
                "trace_id": str(handle.run_id),
                "operation": "end",
                "active": handle.active,
                "status": status,
                **safe,
            }
        )


def _has_trace(case: dict[str, object]) -> bool:
    trace_count = case.get("trace_count")
    return isinstance(trace_count, int) and trace_count >= 1


def _previous_day_news() -> InMemoryDailyNewsService:
    observed = datetime.now(UTC)
    published = observed.replace(hour=12, minute=0, second=0, microsecond=0) - timedelta(days=1)
    payload = f"""<rss><channel><item><title>ATLAS live evidence signal</title>
    <link>https://example.com/atlas-live-signal</link>
    <pubDate>{published.strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
    <description>Bounded technical signal for the live trace fixture.</description></item></channel></rss>"""
    candidates = parse_feed(
        payload.encode(),
        publisher="ATLAS fixture publisher",
        captured_at=observed,
        authority_score=0.95,
        topic_score=0.95,
    )
    return InMemoryDailyNewsService(candidates)


def _plan(client: TestClient, tool_id: str, *, actor_id: str = "anonymous") -> dict[str, Any]:
    inputs = {"resource_id": "fixture-resource"} if tool_id == "private_delete" else {}
    response = client.post(
        "/v1/agent/plans",
        json={
            "request": f"Live trace fixture for {tool_id}",
            "selected_tool": tool_id,
            "input": inputs,
            "actor_id": actor_id,
        },
    )
    response.raise_for_status()
    return response.json()


def _journey(
    name: str,
    client: TestClient,
    sink: RecordingTraceSink,
    action: Any,
) -> dict[str, object]:
    before = len(sink.records)
    started = time.perf_counter()
    result = action()
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    response = result if hasattr(result, "status_code") else None
    body = result.json() if response is not None and result.content else result
    events = body.get("events", []) if isinstance(body, dict) else []
    outcome = body.get("status", "unknown") if isinstance(body, dict) else "unknown"
    if any(event.get("status") == "failed" for event in events if isinstance(event, dict)):
        outcome = "failed"
    elif any(event.get("status") == "abstained" for event in events if isinstance(event, dict)):
        outcome = "abstained"
    elif name == "resumed":
        outcome = "resumed"
    if response is not None and response.status_code >= 400:
        outcome = "rejected"
    traces = sink.records[before:]
    return {
        "case_id": name,
        "http_status": response.status_code if response is not None else 200,
        "run_id": body.get("run_id") if isinstance(body, dict) else None,
        "outcome": outcome,
        "latency_ms": elapsed_ms,
        "trace_count": sum(record.get("status") == "started" for record in traces),
        "traces": traces,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evals/results/agent-tool-live-evidence.json"),
    )
    args = parser.parse_args()
    sink = RecordingTraceSink(
        # create_app uses this injected sink for agent lifecycle traces.
        __import__("atlas.observability.langsmith", fromlist=["LangSmithTraceSink"])
        .LangSmithTraceSink.from_settings(get_settings())
    )
    results: list[dict[str, object]] = []

    with TestClient(create_app(news_service=_previous_day_news(), news_trace_sink=sink)) as client:
        results.append(
            _journey(
                "successful",
                client,
                sink,
                lambda: client.post(
                    "/v1/agent/runs",
                    json={"plan_hash": _plan(client, "daily_news")["plan_hash"]},
                ),
            )
        )

        no_news = TestClient(create_app(news_service=InMemoryDailyNewsService(), news_trace_sink=sink))
        with no_news:
            results.append(
                _journey(
                    "abstained",
                    no_news,
                    sink,
                    lambda: no_news.post(
                        "/v1/agent/runs",
                        json={"plan_hash": _plan(no_news, "daily_news")["plan_hash"]},
                    ),
                )
            )

        private = _plan(client, "private_delete")
        results.append(
            _journey(
                "rejected",
                client,
                sink,
                lambda: client.post(
                    "/v1/agent/runs",
                    json={
                        "plan_hash": private["plan_hash"],
                        "actor_id": "different-owner",
                        "approval_ids": private["required_approval_ids"],
                    },
                ),
            )
        )

        failing_service = type("FailingNews", (), {"get_daily": lambda self: (_ for _ in ()).throw(RuntimeError("fixture failure"))})()
        failing = TestClient(create_app(news_service=failing_service, news_trace_sink=sink))
        with failing:
            results.append(
                _journey(
                    "failed",
                    failing,
                    sink,
                    lambda: failing.post(
                        "/v1/agent/runs",
                        json={"plan_hash": _plan(failing, "daily_news")["plan_hash"]},
                    ),
                )
            )

        pending = _plan(client, "private_delete")
        run = client.post("/v1/agent/runs", json={"plan_hash": pending["plan_hash"]}).json()
        run_id = UUID(run["run_id"])
        results.append(
            _journey(
                "cancelled",
                client,
                sink,
                lambda: client.post(f"/v1/agent/runs/{run_id}/cancel"),
            )
        )
        results.append(
            _journey(
                "resumed",
                client,
                sink,
                lambda: client.post(f"/v1/agent/runs/{run_id}/resume"),
            )
        )

    output = {
        "artifact_type": "atlas.agent_live_trace_evidence",
        "generated_at": datetime.now(UTC).isoformat(),
        "trace_backend": "LangSmith-compatible sink",
        "content_policy": "opaque IDs and bounded metrics only; no private content",
        "cases": results,
        "status": "passed"
        if all(_has_trace(case) for case in results)
        else "partial",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # This CLI is an evidence producer; its output is validated and reviewed before commit.
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": output["status"], "cases": len(results)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
