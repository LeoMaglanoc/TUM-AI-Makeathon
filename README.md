# TUM.AI Makeathon — LLM Chat

Streaming chat app powered by Gemini. Python (FastAPI) backend + Next.js frontend.

## Quick start

```bash
# 1. Copy env and add your Gemini API key
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your-actual-key

# 2. Start both services
make up

# 3. Open http://localhost:3000
```

## Commands

```bash
make up       # Build and start backend (:8000) + frontend (:3000)
make down     # Stop all services
make test     # Run all backend tests
make lint     # Run ruff linter
make format   # Auto-format Python code
```

## Architecture

See [docs/architecture.md](docs/architecture.md).

```
Browser (:3000) → POST /api/chat → FastAPI (:8000) → Gemini API → SSE stream back
```

## Docs

- [Architecture](docs/architecture.md)
- [Requirements](docs/requirements.md)
- [Failure modes](docs/failure-modes.md)
- [AI role](docs/ai-role.md)
- [Testing](docs/testing.md)
- [Plan](docs/plan.md)
