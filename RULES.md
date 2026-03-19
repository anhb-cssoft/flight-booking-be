# Coding Rules & Standards

## 1. Pydantic Modeling
- Always use `BaseModel` from `pydantic`.
- Use `alias_generator` to automatically convert `snake_case` (Python) to `camelCase` (JSON) for external responses.
- Use `Field(..., validation_alias=...)` to accurately map fields from the messy Legacy API.

## 2. API Design
- **RESTful**: URLs must use plural nouns, separated by hyphens (kebab-case).
- **Versioning**: Prefix all routes with `/api/v1/...`.
- **Response Shape**: All successful responses must be wrapped in an object (avoid returning raw arrays at the root).

## 3. Resilience Pattern
- **Timeout**: Default 5s for all Legacy API calls.
- **Retry**: Only retry on 5xx errors or Network errors (using `tenacity`).
- **Circuit Breaker**: Prevent cascade failures when the Legacy API is completely down (simulated via `simulate_issues=true`).

## 4. Documentation
- Every endpoint must have a `summary`, `description`, and `response_model`.
- Write Google-style Docstrings for critical logic functions.

## 5. Security
- Never commit `.env` files containing sensitive API keys or base URLs.
- Perform strict input validation (Pydantic) before forwarding data to the Legacy API.
