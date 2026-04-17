"""Provider factory — returns the stream_chat function for a given LLM provider."""

from collections.abc import Callable, Generator


def get_stream_chat(provider: str) -> Callable[..., Generator[str, None, None]]:
    if provider == "openai":
        from src.ai.openai_provider import stream_chat

        return stream_chat
    from src.ai.gemini import stream_chat

    return stream_chat
