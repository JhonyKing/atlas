from datetime import timedelta
from typing import cast
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider
from atlas.persistence.agent_quota import InMemoryAgentToolQuotaRepository


def _authenticated_client(*, quota_limit: int = 5) -> tuple[TestClient, UUID, dict[str, str]]:
    subject_id = UUID("00000000-0000-0000-0000-000000000001")
    client = TestClient(
        create_app(
            auth_provider=FakeAuthProvider(
                {"ana@example.test": ("correct horse", subject_id)}
            ),
            agent_quota_repository=InMemoryAgentToolQuotaRepository(
                limit=quota_limit, window=timedelta(hours=24)
            ),
        )
    )
    client.post(
        "/v1/auth/session",
        json={"email": "ana@example.test", "password": "correct horse"},
    )
    session_token = client.cookies.get("atlas_session")
    assert session_token
    client.cookies.clear()
    client.cookies.set("atlas_visitor", "v" * 32)
    return client, subject_id, {"Authorization": f"Bearer {session_token}"}


def _approved_plan(
    client: TestClient,
    subject_id: UUID,
    auth_headers: dict[str, str],
    operation_key: str,
) -> tuple[dict[str, object], str]:
    headers = {**auth_headers, "Idempotency-Key": operation_key}
    plan_response = client.post(
        "/v1/agent/plans",
        json={
            "request": "Review this publication",
            "selected_tool": "human_review",
            "input": {},
            "actor_id": str(subject_id),
        },
        headers=headers,
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()
    approval_id = plan["required_approval_ids"][0]
    decision = client.post(
        f"/v1/agent/approvals/{approval_id}/decision",
        json={
            "actor_id": str(subject_id),
            "decision": "approved",
            "decision_key": plan["approval_decision_keys"][approval_id],
        },
        headers=headers,
    )
    assert decision.status_code == 200
    return plan, approval_id


def test_side_effect_plan_and_approval_require_one_bound_operation_key() -> None:
    client, subject_id, auth_headers = _authenticated_client()
    body = {
        "request": "Review this publication",
        "selected_tool": "human_review",
        "input": {},
        "actor_id": str(subject_id),
    }

    missing = client.post("/v1/agent/plans", json=body, headers=auth_headers)
    assert missing.status_code == 400

    operation_key = "operation-key-001"
    plan = client.post(
        "/v1/agent/plans",
        json=body,
        headers={**auth_headers, "Idempotency-Key": operation_key},
    ).json()
    approval_id = plan["required_approval_ids"][0]
    decision_body = {
        "actor_id": str(subject_id),
        "decision": "approved",
        "decision_key": plan["approval_decision_keys"][approval_id],
    }

    missing_decision_key = client.post(
        f"/v1/agent/approvals/{approval_id}/decision",
        json=decision_body,
        headers=auth_headers,
    )
    assert missing_decision_key.status_code == 400
    wrong_decision_key = client.post(
        f"/v1/agent/approvals/{approval_id}/decision",
        json=decision_body,
        headers={**auth_headers, "Idempotency-Key": "operation-key-002"},
    )
    assert wrong_decision_key.status_code == 403
    approved = client.post(
        f"/v1/agent/approvals/{approval_id}/decision",
        json=decision_body,
        headers={**auth_headers, "Idempotency-Key": operation_key},
    )
    assert approved.status_code == 200

    wrong_run_key = client.post(
        "/v1/agent/runs",
        json={
            "plan_hash": plan["plan_hash"],
            "actor_id": str(subject_id),
            "approval_ids": [approval_id],
            "consent": True,
        },
        headers={**auth_headers, "Idempotency-Key": "operation-key-002"},
    )
    assert wrong_run_key.status_code == 403


def test_side_effect_quota_blocks_a_new_operation_before_adapter_execution() -> None:
    client, subject_id, auth_headers = _authenticated_client(quota_limit=1)
    first_plan, first_approval = _approved_plan(
        client, subject_id, auth_headers, "operation-key-001"
    )
    first = client.post(
        "/v1/agent/runs",
        json={
            "plan_hash": first_plan["plan_hash"],
            "actor_id": str(subject_id),
            "approval_ids": [first_approval],
            "consent": True,
        },
        headers={**auth_headers, "Idempotency-Key": "operation-key-001"},
    )
    assert first.status_code == 202

    second_plan, second_approval = _approved_plan(
        client, subject_id, auth_headers, "operation-key-002"
    )
    second = client.post(
        "/v1/agent/runs",
        json={
            "plan_hash": second_plan["plan_hash"],
            "actor_id": str(subject_id),
            "approval_ids": [second_approval],
            "consent": True,
        },
        headers={**auth_headers, "Idempotency-Key": "operation-key-002"},
    )

    assert second.status_code == 429
    assert second.headers["Retry-After"]
    call = cast(FastAPI, client.app).state.agent_run_repository.get_tool_call(
        UUID(second.json()["detail"]["run_id"]), "step-0"
    )
    assert call is not None
    assert call["error_category"] == "quota_exhausted"
