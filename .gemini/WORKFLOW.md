# Project Development Workflow

All steps must be reflected in Git Commits corresponding to each sub-task.

## Phase 1: Setup & Scaffolding (15-30m)
- Initialize `app/` directory according to Layered Architecture.
- Configure `pyproject.toml` (FastAPI, uvicorn, httpx, pydantic-settings, tenacity).
- Implement boilerplate `main.py`.

## Phase 2: Legacy Client & Base Resilience (1h)
- Build `LegacyAPIClient` using `httpx.AsyncClient`.
- Implement retry logic with `tenacity`.
- Define Base Error Transformer (unifying 4 legacy error types).

## Phase 3: Flight Search - Core Feature (2h)
- Reverse-engineer Legacy `/api/v1/flightsearch`.
- Design **Downstream Schema**: Flat, lean, and cleaned of noise.
- Implement `SearchService`: Flattening + Labeling (e.g., MH -> Malaysia Airlines).
- Implement Wrapper-level Pagination (Legacy lacks it).

## Phase 4: Booking Flow (2h)
- Implement `/api/v1/offers/{id}` and `/api/v1/bookings`.
- Ensure strict input validation for booking requests.
- Mock complex responses for edge-case testing.

## Phase 5: Caching & Airport Metadata (1h)
- Implement caching layer for `/api/airports`.
- Merge data from List Airport and Single Airport (Legacy omits city names in the list).

## Phase 6: Final Polish & Documentation (1h)
- Review Swagger UI for consistency.
- Write architecture documentation (main README.md).
- Verify resilience patterns with `?simulate_issues=true`.
