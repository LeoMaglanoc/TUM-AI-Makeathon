"""Unit tests for the Gemini client wrapper (mocked SDK)."""

from unittest.mock import MagicMock, patch

from src.ai.gemini import stream_chat
from src.core.types import Message


def _make_chunk(text: str):
    """Create a mock Gemini SDK response chunk."""
    chunk = MagicMock()
    chunk.text = text
    return chunk


def _make_empty_chunk():
    """Create a mock chunk with no text."""
    chunk = MagicMock()
    chunk.text = None
    return chunk


class TestStreamChat:
    @patch("src.ai.gemini.genai")
    def test_yields_sse_lines(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content_stream.return_value = iter(
            [_make_chunk("Hello"), _make_chunk(" world")]
        )

        messages = [Message(role="user", content="Hi")]
        lines = list(stream_chat(messages, api_key="fake-key"))

        assert lines[0] == 'data: {"token": "Hello"}\n\n'
        assert lines[1] == 'data: {"token": " world"}\n\n'
        assert lines[-1] == "data: [DONE]\n\n"

    @patch("src.ai.gemini.genai")
    def test_skips_empty_chunks(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content_stream.return_value = iter(
            [_make_empty_chunk(), _make_chunk("ok"), _make_empty_chunk()]
        )

        messages = [Message(role="user", content="Hi")]
        lines = list(stream_chat(messages, api_key="fake-key"))

        assert lines[0] == 'data: {"token": "ok"}\n\n'
        assert lines[1] == "data: [DONE]\n\n"
        assert len(lines) == 2

    @patch("src.ai.gemini.genai")
    def test_maps_assistant_to_model_role(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content_stream.return_value = iter(
            [_make_chunk("hi")]
        )

        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there"),
            Message(role="user", content="How are you?"),
        ]
        list(stream_chat(messages, api_key="fake-key"))

        call_args = mock_client.models.generate_content_stream.call_args
        contents = call_args.kwargs["contents"]
        assert contents[1]["role"] == "model"

    @patch("src.ai.gemini.genai")
    def test_uses_custom_model(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content_stream.return_value = iter(
            [_make_chunk("hi")]
        )

        messages = [Message(role="user", content="Hi")]
        list(stream_chat(messages, api_key="fake-key", model="gemini-3-pro-preview"))

        call_args = mock_client.models.generate_content_stream.call_args
        assert call_args.kwargs["model"] == "gemini-3-pro-preview"

    @patch("src.ai.gemini.genai")
    def test_uses_default_model(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content_stream.return_value = iter(
            [_make_chunk("hi")]
        )

        messages = [Message(role="user", content="Hi")]
        list(stream_chat(messages, api_key="fake-key"))

        call_args = mock_client.models.generate_content_stream.call_args
        assert call_args.kwargs["model"] == "gemini-2.0-flash"

    @patch("src.ai.gemini.genai")
    def test_raises_on_sdk_error(self, mock_genai):
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content_stream.side_effect = Exception("API error")

        messages = [Message(role="user", content="Hi")]
        import pytest

        with pytest.raises(Exception, match="API error"):
            list(stream_chat(messages, api_key="fake-key"))
