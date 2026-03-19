from typing import Optional
from fastapi import APIRouter
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
async def create_booking(request: bff_schemas.BookingRequest, simulate_issues: Optional[bool] = None):
    return await booking_service.create_booking(request, simulate_issues=simulate_issues)

@router.get("/{ref}", response_model=bff_schemas.BookingResponse)
async def get_booking(ref: str, simulate_issues: Optional[bool] = None):
    return await booking_service.get_booking(ref, simulate_issues=simulate_issues)
