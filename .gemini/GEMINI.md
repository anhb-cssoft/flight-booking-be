# Project Mandates: Flight Booking BFF (FastAPI)

You are a Senior Backend Engineer performing a technical assessment. All actions must demonstrate professionalism, clean code, and high-level systemic thinking.

## 1. Architecture
We strictly adhere to a **Layered Architecture**:
- `app/api/`: Endpoint definitions (Routes), request/response schema management (Downstream models).
- `app/services/`: Business logic, data orchestration between clients, and data transformation.
- `app/clients/`: `LegacyAPIClient` responsible for calling the upstream system. Definitions of Pydantic models for raw data (Upstream models).
- `app/core/`: System configuration, logging, security, and shared utilities (resilience, caching).

## 2. Coding Standards
- **Transformation First**: Upstream (Legacy) models must never leak to the Frontend. All legacy data must be transformed into a Flat Structure.
- **Naming Convention**: 
    - Python: `snake_case`.
    - JSON Response: `camelCase` (Use Pydantic configuration for automatic conversion).
- **Date/Time**: All legacy formats must be normalized to **ISO 8601** (`YYYY-MM-DDTHH:mm:ssZ`).
- **Error Handling**: Consolidate the four legacy error formats into a single unified structure:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message",
      "details": {}
    }
  }
  ```
- **Type Hinting**: 100% code coverage with Python Type Hints is mandatory.

## 3. Workflow
1. **Research Phase**: Explore Legacy Swagger.
2. **Contract First**: Define Pydantic models for Downstream (what the Frontend expects).
3. **Client Implementation**: Build the Legacy API client with Resilience (Retry, Timeout).
4. **Service Layer**: Implement "Flattening" and "Labeling" (Code-to-Label mapping).
5. **Validation**: Write Unit/Integration tests for each endpoint.

## 4. AI Workflow Documentation (Mandatory)
Maintain an `AI_WORKFLOW.md` log:
- Which prompts were effective?
- Where did the AI fail, and how did you correct it?
- Tools: Gemini CLI, GitHub Copilot.

## 5. Resilience & Caching
- Use `tenacity` for Retry logic on `503` or `429` errors.
- Implement `LRU Cache` or `Redis` for static metadata (Airports).
