from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from atlas.observability.context import (
    RequestContextMiddleware,
    current_request_id,
)
from atlas.observability.pricing import (
    CostMetrics,
    EffectivePriceTable,
    TokenUsage,
    estimate_cost,
)
from atlas.observability.structured import log_event
from atlas.observability.telemetry import observed_span
from atlas.providers.ports import ModelPrice


def test_request_context_injects_and_propagates_a_uuid_request_id() -> None:
    application = FastAPI()
    application.add_middleware(RequestContextMiddleware)

    @application.get("/context")
    def context() -> dict[str, str]:
        request_id = current_request_id()
        assert request_id is not None
        return {"request_id": str(request_id)}

    client = TestClient(application)
    supplied = uuid4()

    response = client.get("/context", headers={"X-Request-ID": str(supplied)})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == str(supplied)
    assert response.json()["request_id"] == str(supplied)


def test_invalid_request_id_is_replaced_with_a_uuid() -> None:
    application = FastAPI()
    application.add_middleware(RequestContextMiddleware)
    application.get("/")(lambda: {"ok": True})

    response = TestClient(application).get("/", headers={"X-Request-ID": "not-a-uuid"})

    generated = UUID(response.headers["x-request-id"])
    assert generated.version == 4


def test_structured_telemetry_redacts_question_and_evidence_content(caplog) -> None:
    request_id = uuid4()
    with caplog.at_level(logging.INFO, logger="atlas"):
        log_event(
            logging.getLogger("atlas"),
            "answer.generate",
            request_id=request_id,
            fields={
                "question": "How do I deploy?",
                "evidence_excerpt": "secret source text",
                "model": "gpt-5.6-luna",
                "claim_count": 2,
            },
        )

    serialized = caplog.messages[-1]
    assert "How do I deploy?" not in serialized
    assert "secret source text" not in serialized
    assert serialized.count(str(request_id)) == 1
    assert '"atlas.claim_count":2' in serialized
    assert '"atlas.operation":"answer.generate"' in serialized


def test_effective_price_lookup_and_cost_estimate_are_dated_and_reproducible() -> None:
    table = EffectivePriceTable(
        version="prices-v1",
        prices=(
            ModelPrice(
                model_id="gpt-5.6-luna",
                effective_from=datetime(2026, 1, 1, tzinfo=UTC),
                input_per_million=Decimal("1.00"),
                output_per_million=Decimal("2.00"),
                reasoning_per_million=Decimal("3.00"),
                cache_read_per_million=Decimal("0.10"),
                cache_write_per_million=Decimal("0.20"),
            ),
            ModelPrice(
                model_id="gpt-5.6-luna",
                effective_from=datetime(2026, 7, 1, tzinfo=UTC),
                input_per_million=Decimal("1.50"),
                output_per_million=Decimal("2.50"),
                reasoning_per_million=Decimal("3.50"),
                cache_read_per_million=Decimal("0.15"),
                cache_write_per_million=Decimal("0.25"),
            ),
        ),
    )

    old = table.get("gpt-5.6-luna", datetime(2026, 3, 1, tzinfo=UTC))
    new = table.get("gpt-5.6-luna", datetime(2026, 8, 1, tzinfo=UTC))
    estimate = estimate_cost(
        table,
        "gpt-5.6-luna",
        TokenUsage(
            input_tokens=1_000,
            output_tokens=2_000,
            reasoning_tokens=500,
            cached_tokens=200,
            cache_write_tokens=100,
        ),
        observed_at=datetime(2026, 8, 1, tzinfo=UTC),
    )

    assert old is not None and old.input_per_million == Decimal("1.00")
    assert new is not None and new.input_per_million == Decimal("1.50")
    assert estimate.price_table_version == "prices-v1"
    assert estimate.total_usd == Decimal("0.008005")
    metrics = CostMetrics()
    metrics.observe(estimate)
    assert metrics.snapshot() == {"request_count": 1, "total_usd": Decimal("0.008005")}


def test_observed_span_contains_only_safe_metrics() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("atlas.tests")
    request_id = uuid4()

    with observed_span(
        tracer,
        "retrieval.search",
        request_id=request_id,
        fields={"question": "private", "candidate_count": 8},
    ) as span:
        span.set_attribute("atlas.test", "ok")

    finished = exporter.get_finished_spans()[0]
    attributes = finished.attributes
    assert attributes is not None
    assert attributes["atlas.request_id"] == str(request_id)
    assert attributes["atlas.candidate_count"] == 8
    assert "question" not in attributes
    assert "private" not in str(attributes)
