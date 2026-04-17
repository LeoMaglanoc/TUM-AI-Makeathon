"""Unit tests for the OpenAI provider (mocked SDK)."""

from unittest.mock import MagicMock, patch

from src.ai.openai_provider import DEFAULT_MODEL, _to_openai_messages, stream_chat
from src.core.types import Message


def _make_chunk(content):
    chunk = MagicMock()
    chunk.choices[0].delta.content = content
    return chunk


def _make_client_mock(chunks):
    client_mock = MagicMock()
    client_mock.chat.completions.create.return_value = iter(chunks)
    return client_mock


@patch("src.ai.openai_provider.openai.OpenAI")
def test_stream_chat_yields_sse_lines(mock_openai_cls):
    chunks = [_make_chunk("Hello"), _make_chunk(" world")]
    mock_openai_cls.return_value = _make_client_mock(chunks)

    messages = [Message(role="user", content="Hi")]
    result = list(stream_chat(messages, api_key="test-key"))

    assert result[0] == 'data: {"token": "Hello"}\n\n'
    assert result[1] == 'data: {"token": " world"}\n\n'
    assert result[-1] == "data: [DONE]\n\n"


@patch("src.ai.openai_provider.openai.OpenAI")
def test_stream_chat_skips_none_content(mock_openai_cls):
    chunks = [_make_chunk(None), _make_chunk("Hi"), _make_chunk(None)]
    mock_openai_cls.return_value = _make_client_mock(chunks)

    result = list(stream_chat([Message(role="user", content="test")], api_key="key"))

    data_lines = [line for line in result if line != "data: [DONE]\n\n"]
    assert len(data_lines) == 1
    assert '"token": "Hi"' in data_lines[0]


@patch("src.ai.openai_provider.openai.OpenAI")
def test_stream_chat_uses_default_model(mock_openai_cls):
    client_mock = _make_client_mock([])
    mock_openai_cls.return_value = client_mock

    list(stream_chat([Message(role="user", content="hi")], api_key="key"))

    _, kwargs = client_mock.chat.completions.create.call_args
    assert kwargs["model"] == DEFAULT_MODEL


@patch("src.ai.openai_provider.openai.OpenAI")
def test_stream_chat_uses_custom_model(mock_openai_cls):
    client_mock = _make_client_mock([])
    mock_openai_cls.return_value = client_mock

    list(stream_chat([Message(role="user", content="hi")], api_key="key", model="gpt-4o"))

    _, kwargs = client_mock.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o"


def test_to_openai_messages_role_passthrough():
    messages = [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there"),
    ]
    result = _to_openai_messages(messages)
    assert result == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]


@patch("src.ai.openai_provider.openai.OpenAI")
def test_stream_chat_terminates_with_done(mock_openai_cls):
    mock_openai_cls.return_value = _make_client_mock([])

    result = list(stream_chat([Message(role="user", content="hi")], api_key="key"))

    assert result == ["data: [DONE]\n\n"]
