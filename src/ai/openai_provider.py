"""OpenAI client wrapper — sync generator yielding SSE-formatted chunks."""

import json
from collections.abc import Generator

import openai

from src.core.types import Message

DEFAULT_MODEL = "gpt-4o-mini"


def _to_openai_messages(messages: list[Message]) -> list[dict]:
    return [{"role": msg.role, "content": msg.content} for msg in messages]


def stream_chat(
    messages: list[Message], *, api_key: str, model: str = DEFAULT_MODEL
) -> Generator[str, None, None]:
    """Stream a chat response from OpenAI, yielding SSE-formatted lines."""
    client = openai.OpenAI(api_key=api_key)
    openai_messages = _to_openai_messages(messages)

    for chunk in client.chat.completions.create(
        model=model, messages=openai_messages, stream=True
    ):
        content = chunk.choices[0].delta.content
        if content:
            yield f"data: {json.dumps({'token': content})}\n\n"

    yield "data: [DONE]\n\n"
