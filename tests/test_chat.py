"""Integration tests for the /api/chat endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
@patch("src.main.get_stream_chat")
@patch("src.main.GEMINI_API_KEY", "fake-key")
@patch("src.main.LLM_PROVIDER", "gemini")
async def test_chat_returns_sse_stream(mock_get_stream_chat):
    mock_get_stream_chat.return_value = lambda msgs, **kw: iter(
        ['data: {"token": "Hi"}\n\n', "data: [DONE]\n\n"]
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert 'data: {"token": "Hi"}' in resp.text
    assert "data: [DONE]" in resp.text


@pytest.mark.anyio
async def test_chat_rejects_empty_messages():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/chat", json={"messages": []})
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_chat_rejects_invalid_role():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "system", "content": "bad"}]},
        )
    assert resp.status_code == 422


@pytest.mark.anyio
@patch("src.main.LLM_PROVIDER", "gemini")
@patch("src.main.GEMINI_API_KEY", "")
async def test_chat_returns_503_when_no_gemini_key():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )
    assert resp.status_code == 503
    assert "No API key" in resp.json()["detail"]


@pytest.mark.anyio
@patch("src.main.LLM_PROVIDER", "openai")
@patch("src.main.OPENAI_API_KEY", "")
async def test_chat_returns_503_when_no_openai_key():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )
    assert resp.status_code == 503
    assert "No API key" in resp.json()["detail"]


@pytest.mark.anyio
@patch("src.main.get_stream_chat")
@patch("src.main.GEMINI_API_KEY", "fake-key")
@patch("src.main.LLM_PROVIDER", "gemini")
async def test_chat_returns_500_on_llm_error(mock_get_stream_chat):
    mock_stream_fn = MagicMock(side_effect=Exception("provider exploded"))
    mock_get_stream_chat.return_value = mock_stream_fn
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )
    assert resp.status_code == 500
    assert "LLM error" in resp.json()["detail"]


@pytest.mark.anyio
@patch("src.main.get_stream_chat")
@patch("src.main.LLM_MODEL", "gpt-4o")
@patch("src.main.GEMINI_API_KEY", "fake-key")
@patch("src.main.LLM_PROVIDER", "gemini")
async def test_chat_passes_model_from_env(mock_get_stream_chat):
    mock_stream_fn = MagicMock(return_value=iter(["data: [DONE]\n\n"]))
    mock_get_stream_chat.return_value = mock_stream_fn
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )
    _, kwargs = mock_stream_fn.call_args
    assert kwargs["model"] == "gpt-4o"


@pytest.mark.anyio
@patch("src.main.get_stream_chat")
@patch("src.main.LLM_MODEL", "")
@patch("src.main.GEMINI_API_KEY", "fake-key")
@patch("src.main.LLM_PROVIDER", "gemini")
async def test_chat_uses_default_model_when_env_empty(mock_get_stream_chat):
    mock_stream_fn = MagicMock(return_value=iter(["data: [DONE]\n\n"]))
    mock_get_stream_chat.return_value = mock_stream_fn
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )
    _, kwargs = mock_stream_fn.call_args
    assert "model" not in kwargs


@pytest.mark.anyio
@patch("src.main.get_stream_chat")
@patch("src.main.LLM_PROVIDER", "openai")
@patch("src.main.OPENAI_API_KEY", "fake-openai-key")
async def test_chat_openai_provider_routes(mock_get_stream_chat):
    mock_get_stream_chat.return_value = lambda msgs, **kw: iter(
        ['data: {"token": "Hi"}\n\n', "data: [DONE]\n\n"]
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    mock_get_stream_chat.assert_called_with("openai")


@pytest.mark.anyio
@patch("src.main.get_stream_chat")
@patch("src.main.GEMINI_API_KEY", "")
@patch("src.main.LLM_PROVIDER", "gemini")
async def test_chat_uses_api_key_from_request_body(mock_get_stream_chat):
    mock_get_stream_chat.return_value = lambda msgs, **kw: iter(["data: [DONE]\n\n"])
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi"}], "api_key": "from-browser"},
        )
    assert resp.status_code == 200


@pytest.mark.anyio
@patch("src.main.get_stream_chat")
@patch("src.main.GEMINI_API_KEY", "env-gemini-key")
@patch("src.main.OPENAI_API_KEY", "")
@patch("src.main.LLM_PROVIDER", "gemini")
async def test_chat_request_provider_overrides_env(mock_get_stream_chat):
    mock_get_stream_chat.return_value = lambda msgs, **kw: iter(["data: [DONE]\n\n"])
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "provider": "openai",
                "api_key": "from-browser-openai",
            },
        )
    mock_get_stream_chat.assert_called_with("openai")


@pytest.mark.anyio
@patch("src.main.GEMINI_API_KEY", "")
@patch("src.main.OPENAI_API_KEY", "")
@patch("src.main.LLM_PROVIDER", "gemini")
async def test_chat_returns_503_when_no_key_anywhere():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )
    assert resp.status_code == 503
    assert "No API key" in resp.json()["detail"]
