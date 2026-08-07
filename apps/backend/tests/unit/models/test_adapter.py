import pytest

from atlas.models import ModelRequest, ModelSelection
from atlas.providers.model_adapter import DeterministicModelAdapter


@pytest.mark.asyncio
async def test_common_adapter_returns_typed_response_without_sdk_details() -> None:
    response = await DeterministicModelAdapter().generate(
        ModelRequest(
            prompt="hello",
            selection=ModelSelection("demo", "gpt-5.6-luna", "low", "test", "fixture"),
            request_id="run-1",
        ),
        evidence=[],
    )
    assert response.text == "hello"
    assert response.provider_request_id is None
