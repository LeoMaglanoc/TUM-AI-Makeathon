# Failure Modes

## A) Missing API key

- **Symptom**: `GEMINI_API_KEY` env var not set or empty.
- **Handling**: Backend returns HTTP 503 with `"GEMINI_API_KEY not set"`.
- **Test**: `test_chat_returns_503_when_no_api_key`

## B) Gemini SDK error

- **Symptom**: Network failure, quota exceeded, invalid key.
- **Handling**: Backend returns HTTP 500 with `"Gemini error: ..."`.
- **Test**: `test_chat_returns_500_on_gemini_error`

## C) Invalid request

- **Symptom**: Empty messages, invalid role, missing fields.
- **Handling**: Pydantic validation → HTTP 422 with details.
- **Tests**: `test_chat_rejects_empty_messages`, `test_chat_rejects_invalid_role`

## D) Client abort

- **Symptom**: User clicks "Stop" or navigates away.
- **Handling**: `AbortController` cancels the fetch; frontend stops updating.

## E) Network instability

- **Symptom**: Partial stream, connection drop.
- **Handling**: Frontend shows partial assistant message + connection error.
