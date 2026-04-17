"""Gemini client wrapper — sync generator yielding SSE-formatted chunks."""

import json
from collections.abc import Generator

from google import genai

from src.core.types import Message

DEFAULT_MODEL = "gemini-2.0-flash"


def _to_gemini_contents(messages: list[Message]) -> list[dict]:
    """Convert our Message list to Gemini SDK content format.

    Maps 'assistant' role to 'model' as required by the Gemini API.
    """
    contents = []
    for msg in messages:
        role = "model" if msg.role == "assistant" else msg.role
        contents.append({"role": role, "parts": [{"text": msg.content}]})
    return contents


def stream_chat(
    messages: list[Message], *, api_key: str, model: str = DEFAULT_MODEL
) -> Generator[str, None, None]:
    """Stream a chat response from Gemini, yielding SSE-formatted lines."""
    client = genai.Client(api_key=api_key)
    contents = _to_gemini_contents(messages)

    for chunk in client.models.generate_content_stream(
        model=model, contents=contents
    ):
        if chunk.text:
            yield f"data: {json.dumps({'token': chunk.text})}\n\n"

    yield "data: [DONE]\n\n"
