from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import flights, bookings, airports

app = FastAPI(
    title="Flight Booking BFF API",
    description="A clean, modern wrapper for the legacy flight data system.",
    version="1.0.0",
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
