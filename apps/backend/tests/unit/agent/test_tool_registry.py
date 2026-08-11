from fastapi.testclient import TestClient

from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolDefinition, ToolLocalization
from atlas.api.main import create_app


def test_default_catalog_contains_core_atlas_capabilities() -> None:
    catalog = ToolCatalog.default()
    tool_ids = {tool.tool_id for tool in catalog.list_for_locale("es-MX")}

    assert {
        "cited_answer",
        "comparison",
        "report",
        "daily_news",
        "corpus_status",
        "private_resources",
        "private_upload",
        "private_delete",
        "human_review",
    } <= tool_ids


def test_catalog_definitions_have_strict_policy_metadata() -> None:
    for tool in ToolCatalog.default().list_for_locale("en-US"):
        assert tool.version
        assert tool.input_schema["type"] == "object"
        assert tool.output_schema["type"] == "object"
        assert tool.side_effect_level in {"read", "private_read", "mutate", "publish", "delete"}
        assert tool.approval in {"none", "explicit_user", "human_reviewer"}
        assert tool.timeout_ms > 0
        assert tool.budget["max_calls"] > 0


def test_catalog_endpoint_is_localized_and_does_not_expose_secrets() -> None:
    client = TestClient(create_app())

    response = client.get("/v1/agent/tools", params={"locale": "es-MX"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == "1.0.0"
    cited_answer = next(item for item in payload["tools"] if item["tool_id"] == "cited_answer")
    assert cited_answer["name"] == "Respuesta con citas"
    assert "api_key" not in response.text.lower()


def test_tool_definition_rejects_unknown_fields() -> None:
    try:
        ToolDefinition(
            tool_id="bad",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            scopes=(),
            side_effect_level="read",
            approval="none",
            timeout_ms=1,
            budget={"max_calls": 1},
            localization={
                "en-US": ToolLocalization(name="Bad", description="Bad"),
                "es-MX": ToolLocalization(name="Mala", description="Mala"),
            },
            unknown="secret",  # type: ignore[call-arg]
        )
    except ValueError:
        return
    raise AssertionError("unknown catalog fields must be rejected")
