# Testing

## Commands

All commands run via Docker (see `Makefile`):

```bash
make test           # Run all tests
make test-unit      # Run unit tests only
make test-integration  # Run integration tests only
make lint           # Run ruff linter
make format         # Auto-format with ruff
```

## Test structure

| File | Level | What it tests |
|------|-------|---------------|
| `tests/test_types.py` | Unit | Pydantic validation: valid/invalid roles, empty content, empty messages |
| `tests/test_gemini.py` | Unit | Gemini client with mocked SDK: SSE output, empty chunks, role mapping |
| `tests/test_chat.py` | Integration | FastAPI endpoint: SSE streaming, error paths, validation |

## Approach

- **TDD**: tests written before implementation
- **Mocked SDK**: Gemini API is never called in tests
- **httpx + ASGITransport**: tests the full FastAPI app in-process
