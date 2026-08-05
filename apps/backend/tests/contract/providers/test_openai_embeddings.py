import json

import httpx
import pytest
from openai import AsyncOpenAI

from atlas.providers.openai_embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    EmbeddingAdapterError,
    OpenAIEmbeddingsAdapter,
)


def embedding_payload(*, dimensions: int = EMBEDDING_DIMENSIONS) -> dict[str, object]:
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.125] * dimensions,
            },
            {
                "object": "embedding",
                "index": 1,
                "embedding": [-0.25] * dimensions,
            },
        ],
        "model": EMBEDDING_MODEL,
        "usage": {"prompt_tokens": 12, "total_tokens": 12},
    }


@pytest.mark.asyncio
async def test_embedding_adapter_sends_model_and_dimension_contract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=embedding_payload())

    client = AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    adapter = OpenAIEmbeddingsAdapter(client=client)
    try:
        vectors = await adapter.embed(["first chunk", "second chunk"])
    finally:
        await client.close()

    body = json.loads(requests[0].content)
    assert body["model"] == EMBEDDING_MODEL
    assert body["dimensions"] == EMBEDDING_DIMENSIONS
    assert body["encoding_format"] == "float"
    assert len(vectors) == 2
    assert all(len(vector) == EMBEDDING_DIMENSIONS for vector in vectors)
    assert vectors[0][0] == 0.125
    assert vectors[1][0] == -0.25


@pytest.mark.asyncio
async def test_embedding_adapter_rejects_dimension_mismatch() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=embedding_payload(dimensions=3))

    client = AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    adapter = OpenAIEmbeddingsAdapter(client=client)
    try:
        with pytest.raises(EmbeddingAdapterError, match="dimension"):
            await adapter.embed(["wrong vector", "another wrong vector"])
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_embedding_adapter_rejects_empty_input_and_unordered_results() -> None:
    client = AsyncOpenAI(api_key="test-key", max_retries=0)
    adapter = OpenAIEmbeddingsAdapter(client=client)
    with pytest.raises(ValueError, match="at least one"):
        await adapter.embed([])
    await client.close()

    def unordered_handler(request: httpx.Request) -> httpx.Response:
        payload = embedding_payload()
        data = payload["data"]
        assert isinstance(data, list)
        data[0]["index"] = 1
        return httpx.Response(200, json=payload)

    unordered_client = AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(unordered_handler)),
    )
    unordered_adapter = OpenAIEmbeddingsAdapter(client=unordered_client)
    try:
        with pytest.raises(EmbeddingAdapterError, match="index"):
            await unordered_adapter.embed(["first", "second"])
    finally:
        await unordered_client.close()
