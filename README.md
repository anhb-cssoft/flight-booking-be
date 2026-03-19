# Flight Booking BFF API

This project is a **Backend for Frontend (BFF)** built with **FastAPI**, serving as a clean and modern wrapper for a legacy flight booking system (easyGDS).

## Key Features
- **Data Standardization**: Maps data from chaotic legacy formats to modern RESTful standards.
- **Caching**: Uses `diskcache` to store airport information, minimizing redundant calls to the legacy API.
- **Error Handling**: Unified error response format for the frontend.
- **Async Support**: Leverages `httpx` and `FastAPI` for high performance.

---

## 1. System Requirements
- **Python**: 3.10 or higher.
- **Operating System**: Windows, macOS, or Linux.

## 2. Installation and Setup

### Step 1: Create a Virtual Environment (Recommended)
```bash
python -m venv .venv
# Activate on Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Activate on macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install .
```
If you want to install development tools (tests, linting):
```bash
pip install ".[dev]"
```

### Step 3: Configure Environment Variables
Check the `.env` file in the root directory to ensure the `LEGACY_API_BASE_URL` is correct:
```env
LEGACY_API_BASE_URL=https://mock-travel-api.vercel.app
```

---

## 3. Running the Application

Use the following command to run the server in development mode:
```bash
# Windows (PowerShell)
$env:PYTHONPATH="."
uvicorn app.main:app --reload

# macOS/Linux
PYTHONPATH=. uvicorn app.main:app --reload
```

The server will run by default at: **http://127.0.0.1:8000**

---

## 4. API Documentation (Interactive Docs)
Once the server is running, you can access the following links to view the documentation and test endpoints directly:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 5. Running Tests
To ensure quality and stability, run the test suite using `pytest`:
```bash
# Windows (PowerShell)
$env:PYTHONPATH="."
python -m pytest

# macOS/Linux
PYTHONPATH=. pytest
```

---

## 6. Main Directory Structure
- `app/api/`: Endpoint and schema definitions (data format returned to the frontend).
- `app/clients/`: Client connecting to the legacy API (easyGDS).
- `app/services/`: Business logic and data mapping services.
- `app/core/`: System configuration files.
- `tests/`: Test cases verifying the correctness of the application.
