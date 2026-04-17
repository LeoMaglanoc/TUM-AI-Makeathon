"""FastAPI app — chat proxy to configurable LLM provider with SSE streaming."""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.ai.factory import get_stream_chat
from src.core.types import ChatRequest

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini")
LLM_MODEL = os.environ.get("LLM_MODEL", "")

app = FastAPI(title="hack-nation-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=503, detail="OPENAI_API_KEY not set.")
        api_key = OPENAI_API_KEY
    else:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=503, detail="GEMINI_API_KEY not set.")
        api_key = GEMINI_API_KEY

    try:
        stream_fn = get_stream_chat(LLM_PROVIDER)
        kwargs: dict = {"api_key": api_key}
        if LLM_MODEL:
            kwargs["model"] = LLM_MODEL
        return StreamingResponse(
            stream_fn(req.messages, **kwargs),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}") from e
