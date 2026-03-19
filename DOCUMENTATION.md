# Technical Documentation: Flight Booking BFF

## 1. API Design Decisions

### REST vs GraphQL
- **Decision**: **REST API** (FastAPI).
- **Reasoning**: Given the 6-8 hour timeframe and the specific requirements for a "clean, frontend-friendly API," REST is more direct for mapping the 6 legacy endpoints to 4 streamlined BFF endpoints. FastAPI provides automatic OpenAPI (Swagger) documentation, which is a key requirement for frontend developers.

### URL & Schema Design
- **Philosophy**: "Frontend-First." The schemas are flattened, removing deep nesting (e.g., `data.flight_results.outbound.results` becomes a top-level `outboundOffers`).
- **Naming**: Consistent `camelCase` for JSON responses (via Pydantic's `alias_generator`) and `snake_case` for Python internal logic.
- **Normalization**: All date formats (ISO, Unix, custom strings) are parsed and returned as standard **ISO 8601** (`YYYY-MM-DDTHH:mm:ssZ`).

### Error Response Structure
- All legacy error formats (which were inconsistent) are unified into a single structure:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message",
      "details": {}
    }
  }
  ```

## 2. Architecture Overview

The project follows a **Layered Architecture** to ensure separation of concerns:

1.  **API Layer (`app/api/`)**: Defines the "Downstream" contract (what the frontend sees). Handles request validation and response serialization.
2.  **Service Layer (`app/services/`)**: The "Brain." Responsible for business logic, data transformation (flattening), and code-to-label mapping (e.g., mapping `MH` to `Malaysia Airlines`).
3.  **Client Layer (`app/clients/`)**: The "Adapter." Responsible for "Upstream" communication with the Legacy API. This layer implements resilience patterns.
4.  **Core Layer (`app/core/`)**: Shared configuration, custom exceptions, and system-wide utilities.

**Data Flow**: `Frontend` -> `API Layer` -> `Service Layer` -> `Client Layer` -> `Legacy API`.

## 3. Resilience Patterns

To handle the simulated instability (`?simulate_issues=true`), the following patterns were implemented in the Client Layer:

- **Retries with Exponential Backoff**: Uses `tenacity` to automatically retry requests that fail with `503` (Service Unavailable) or `429` (Rate Limit). It waits `1s`, then `2s`, then `4s` before giving up.
- **Circuit Breaker**: Implemented a state-based circuit breaker. If the legacy API fails 5 times consecutively, the circuit "opens," and all subsequent requests are rejected immediately for 30 seconds to prevent "hanging" the BFF and to give the legacy system time to recover.
- **Concurrency Control**: Used `asyncio.Semaphore` in the Airport Service to limit the number of parallel requests to the legacy system, preventing `429` errors during mass data fetching.
- **Fail-Fast**: If the Circuit Breaker is open, the system returns a `503` error instantly, avoiding the 15-30s wait times typical of failing legacy systems.

## 4. Caching Strategy

- **What**: Airport metadata (list and details). This data is static and expensive to fetch (N+1 problem in the legacy API).
- **Where**: `diskcache` (Persistent file-based cache in `.cache/`).
- **Invalidation**: TTL (Time-To-Live) set to **24 hours**.
- **Simulation Mode**: When `simulate_issues=true` is passed, the cache is **bypassed** to allow developers to test resilience patterns directly against the unstable legacy system.

## 5. AI Workflow

This project was developed with a high-degree of AI assistance to accelerate implementation while maintaining high standards:

- **ChatGPT**: Used for **clarifying requirements**, analyzing the complex business logic of flight booking, and **double-checking the mapping** between the Legacy API responses and the new BFF schemas to ensure no data was lost during flattening.
- **Gemini (via Gemini CLI)**: Used for **brainstorming** the architecture, creating the **implementation plan**, managing **sub-tasks**, and **writing the actual code**. Gemini's ability to browse and modify the local codebase directly was critical for surgical refactoring and implementing the resilience patterns.

## 6. Setup Instructions

### Prerequisites
- Python 3.10+
- `pip`

### Steps
1.  **Clone the repository**.
2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\Activate.ps1
    # macOS/Linux:
    source .venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install .
    ```
4.  **Run the application**:
    ```bash
    # Windows:
    $env:PYTHONPATH="."
    uvicorn app.main:app --reload
    ```
5.  **Access Documentation**:
    Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test the API. Append `simulate_issues=true` to any request to test resilience.
