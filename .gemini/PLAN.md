# Development Plan: Flight Booking BFF

This document outlines the strategic approach and task breakdown for building the modern API wrapper over the legacy flight system.

## 1. Technical Strategy

### Architecture: Layered Approach
- **API Layer (`app/api`)**: Defines RESTful endpoints and Pydantic schemas for the Frontend (Downstream).
- **Service Layer (`app/services`)**: The "Brain". Handles data transformation, enrichment (code -> label), and orchestration.
- **Client Layer (`app/clients`)**: Handles raw communication with the Legacy API. Defines Pydantic schemas for the legacy response (Upstream).
- **Core Layer (`app/core`)**: Cross-cutting concerns like Resilience (Retry/Timeout), Configuration, and Exception handling.

### Key Technical Choices
- **FastAPI**: High performance, native async support, and excellent OpenAPI generation.
- **Pydantic v2**: Using `alias_generator` for camelCase JSON and `computed_field` for enriched data.
- **HTTPX + Tenacity**: For asynchronous requests and robust retry logic (Exponential Backoff).
- **DiskCache/LRU Cache**: To cache static data like Airport names and city mapping.

---

## 2. Detailed Task List

### Phase 1: Core Foundation & Resilience (EST: 1.5h)
- [ ] **Task 1.1: Configuration System**: Implement `Settings` using `pydantic-settings` to load `.env`.
- [ ] **Task 1.2: Unified Error Handling**: Define a `BaseBFFException` and a global exception handler to catch all 4 legacy error formats and return 1 consistent shape to the FE.
- [ ] **Task 1.3: Resilience Client**: Build a `BaseLegacyClient` using `httpx.AsyncClient` with:
    - Default timeouts (5s).
    - Retry logic using `@retry` from `tenacity` (targeting 503 and 429).
    - Logging of outgoing requests for debugging.

### Phase 2: Airport Metadata & Enrichment (EST: 1h)
- [ ] **Task 2.1: Airport Client**: Implement `get_airports` and `get_airport_by_code`.
- [ ] **Task 2.2: Caching Layer**: Implement a cache for airport data (since it rarely changes).
- [ ] **Task 2.3: Data Merger**: Create a helper to merge "List Airport" and "Single Airport" data to ensure City Names are always available.

### Phase 3: Flight Search & Transformation (EST: 2h)
- [ ] **Task 3.1: Upstream Schemas**: Map the "Deeply Nested" legacy search response.
- [ ] **Task 3.2: Downstream Schemas**: Design the "Flat & Lean" response for the Frontend.
- [ ] **Task 3.3: Search Service**: Implement the flattening logic:
    - Convert `MH` -> `Malaysia Airlines`.
    - Normalize all date formats to ISO 8601.
    - Calculate durations and stops if missing.
- [ ] **Task 3.4: Wrapper Pagination**: Add `limit` and `offset` logic on the BFF side since the legacy API returns everything at once.

### Phase 4: Offer Details & Booking Flow (EST: 2h)
- [ ] **Task 4.1: Offer Details**: Transform the quirky legacy offer response into a clean breakdown of fare rules and baggage.
- [ ] **Task 4.2: Booking Validation**: Implement strict Pydantic validation for passenger details (emails, phone numbers, passport formats).
- [ ] **Task 4.3: Booking Implementation**: Map the booking creation request and unify the response reference.

### Phase 5: Final Polish & Documentation (EST: 1h)
- [ ] **Task 5.1: Swagger Optimization**: Add examples and descriptions to all models for better FE documentation.
- [ ] **Task 5.2: AI Workflow Log**: Complete the `AI_WORKFLOW.md` documenting our process.
- [ ] **Task 5.3: README & Setup**: Finalize instructions on how to run with Docker/Virtualenv.

---

## 3. The "Senior" Edge (Bonus Points)
- **Traceability**: Adding a `X-Request-ID` header to all outgoing legacy calls for better debugging.
- **Graceful Degradation**: If the Airport enrichment fails, return the raw code instead of a 500 error.
- **Performance**: Parallelize "Search" and "Airport Metadata" fetching using `asyncio.gather`.
