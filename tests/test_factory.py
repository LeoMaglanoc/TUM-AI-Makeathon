"""Unit tests for the provider factory."""

from src.ai import gemini, openai_provider
from src.ai.factory import get_stream_chat


def test_returns_gemini_stream_chat():
    assert get_stream_chat("gemini") is gemini.stream_chat


def test_returns_openai_stream_chat():
    assert get_stream_chat("openai") is openai_provider.stream_chat


def test_unknown_provider_falls_back_to_gemini():
    assert get_stream_chat("anthropic") is gemini.stream_chat
