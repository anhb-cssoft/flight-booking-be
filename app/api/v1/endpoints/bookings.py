from fastapi import APIRouter, HTTPException
from app.api.v1.schemas import bookings as bff_schemas
from app.services.bookings import booking_service

router = APIRouter()

@router.post("", response_model=bff_schemas.BookingResponse)
async def create_booking(request: bff_schemas.BookingRequest):
    try:
        return await booking_service.create_booking(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")

@router.get("/{ref}", response_model=bff_schemas.BookingResponse)
async def get_booking(ref: str):
    try:
        return await booking_service.get_booking(ref)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Booking not found: {str(e)}")
