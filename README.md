# Development Process – Flight Booking BFF (FastAPI)

Important note: I have never had the opportunity to work on a real project as a backend developer, with the Python language and FastAPI framework. This project was implemented 100% by collaborating with AI (Gemini CLI, ChatGPT, Perplexity) to analyze requirements, propose architectural solutions, implement source code, write tests, and guide deployment.

## 1. Approach & Thought Process

This service is designed following the **Backend For Frontend (BFF)** model, sitting between the Frontend and the Legacy API system.

I started by analyzing the Swagger/OpenAPI using AI, then applied a research-first approach:

- Identifying issues of the Legacy system:
  - Fragmented data
  - Inconsistent formats
  - Complex nested structures
- Defining the role of the BFF:
  - Data transformation (flattening)
  - Response standardization (ISO date, camelCase)
  - Centralized error handling

The system is divided into modules:

- Flights
- Bookings
- Airports (static data + cache)

---

## 2. Technical Decisions

- **FastAPI**  
  Chosen for high performance (async) and strong type support.  
  → Helps improve reliability and fits well with AI-assisted development.

- **Layered Architecture**
  - `api/` → routes & schema
  - `services/` → business logic & data transformation
  - `clients/` → call legacy API + retry/timeout
  - `core/` → config & error handling

- **Pydantic v2**  
  Validates data and automatically converts snake_case ↔ camelCase.

- **Caching (LRU)**  
  Optimizes access to static data (e.g., airport).

---

## 3. Testing Strategy

Focus on correctness and resilience:

- Integration test with mocked legacy API
- Main cases:
  - Valid / invalid input
  - Handling 503 / 429 errors (retry)
  - Verifying data transformation logic (flattening)
  - Ensuring unified error format

---

## 4. AI Usage

I use AI as a **productivity layer** to accelerate development:

- **ChatGPT / Perplexity**
  - Analyze legacy API
  - Suggest architecture and suitable libraries

- **Gemini CLI**
  - Implement code
  - Generate tests
  - Maintain project structure
  - Refactor and validate logic

## 5. Workflow

1. Analyze API contract (Swagger → Pydantic models)
2. Design layered architecture
3. Implement each module (Flights → Booking)
4. Validate with tests and edge cases
5. Optimize structure and performance

---

## 6. Improvements

- Replace LRU cache with Redis for better scalability
- Integrate OpenTelemetry (tracing)
- Improve logging for debugging legacy system

## 7. Run Instructions

- Requirements:
  - Python 3.10+
  - Virtual environment (venv)

- Steps:

1.  Create and activate virtual environment:
    python -m venv .venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate

2.  Install dependencies:
    pip install -r requirements.txt

3.  Run the application:
    uvicorn app.main:app --reload
    The app will run at: http://localhost:8000
    Visit http://localhost:8000/dos to check the API
