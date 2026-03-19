from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import flights, bookings, airports
from app.core.exceptions import UnifiedError
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Flight Booking BFF API",
    description="A clean, modern wrapper for the legacy flight data system.",
    version="1.0.0",
)

# Exception Handlers
@app.exception_handler(UnifiedError)
async def unified_error_handler(request: Request, exc: UnifiedError):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": {"type": type(exc).__name__} if app.debug else {}
            }
        }
    )

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Flight Booking BFF is running"}

# Include routers
app.include_router(flights.router, prefix="/api/v1/flights", tags=["Flights"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(airports.router, prefix="/api/v1/airports", tags=["Airports"])
