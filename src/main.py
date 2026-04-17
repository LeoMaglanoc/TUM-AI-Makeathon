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

_default_origins = "https://leomaglanoc.github.io,http://localhost:3000,http://127.0.0.1:3000"
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", _default_origins).split(",")]

app = FastAPI(title="tum-ai-makeathon-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    provider = req.provider or LLM_PROVIDER
    if provider == "openai":
        api_key = req.api_key or OPENAI_API_KEY
    else:
        api_key = req.api_key or GEMINI_API_KEY

    if not api_key:
        raise HTTPException(status_code=503, detail="No API key provided.")

    model = req.model or LLM_MODEL or None

    try:
        stream_fn = get_stream_chat(provider)
        kwargs: dict = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return StreamingResponse(
            stream_fn(req.messages, **kwargs),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}") from e
