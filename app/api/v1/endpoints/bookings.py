from fastapi import APIRouter, HTTPException
from app.api.v1.schemas import bookings as bff_schemas
from app.services.bookings import booking_service

router = APIRouter()

@router.post("", 
    response_model=bff_schemas.BookingResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "bookingReference": "EG12FA2A",
                        "pnr": "B96170E",
                        "status": "CONFIRMED",
                        "statusCode": "HK",
                        "offerId": "93f1d242d6fddd80",
                        "passengers": [
                            {
                                "paxId": "PAX1",
                                "title": "Mr",
                                "firstName": "John",
                                "lastName": "Doe",
                                "name": "Doe/John Mr",
                                "dob": "1990-01-01",
                                "nationality": "US",
                                "passportNo": "123456789",
                                "type": "ADT"
                            }
                        ],
                        "contact": {
                            "email": "testuser@gmail.com",
                            "phone": "1234567890"
                        },
                        "ticketing": {
                            "status": "PENDING",
                            "timeLimit": "2026-03-21T06:07:31Z",
                            "ticketNumbers": []
                        },
                        "createdAt": "2026-03-19T11:07:31Z"
                    }
                }
            }
        }
    }
)
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
