# Implementation Plan

## What we built

A Gemini chat web app skeleton: Python (FastAPI) backend + Next.js frontend, streaming SSE, Docker-first.

## What's real vs faked

### Real
- Streaming chat UX (token-by-token rendering)
- Server-side Gemini call (API key hidden from browser)
- Pydantic request validation
- Error handling (missing key, SDK errors, invalid input)
- Abort/cancel (AbortController)
- Docker (both services containerized)
- Tests (18 tests: unit + integration)
- Linting (ruff)

### Faked / deferred
- Rate limiting
- Persistence (in-memory only)
- Auth
- Analytics
- Content moderation

## Extension points
- Add feedback loops (AI role enforcement)
- Add persistence layer
- Add tool use / function calling
- Add multi-model routing
