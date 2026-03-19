from pydantic import BaseModel, EmailStr
from typing import List, Optional
from .flights import FlightOffer

class Passenger(BaseModel):
    first_name: str
    last_name: str
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    passport_no: Optional[str] = None

class BookingRequest(BaseModel):
    offer_id: str
    passengers: List[Passenger]
    contact_email: EmailStr
    contact_phone: Optional[str] = None

class BookingResponse(BaseModel):
    booking_reference: str
    status: str
    total_price: float
    currency: str
    passengers: List[Passenger]
    offer_details: Optional[FlightOffer] = None
