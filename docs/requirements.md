# Requirements

## Functional

1. User types a message and sees a streaming response from Gemini, token-by-token.
2. Multi-turn conversation: the full message history is sent with each request.
3. User can cancel a streaming response mid-flight ("Stop" button).
4. Missing or invalid API key produces a clear error (503).
5. Gemini SDK errors produce a clear error (500).
6. Invalid request payloads are rejected (422).

## Non-functional

- API key never leaves the server (not exposed to browser).
- No conversation persistence (in-memory only).
- Docker-first: everything runs via `docker compose`.
- All backend code linted with `ruff` and tested with `pytest`.
