from pydantic import EmailStr
from typing import List, Optional
from datetime import datetime
from .flights import BaseBFFModel

class PassengerRequest(BaseBFFModel):
    first_name: str
    last_name: str
    title: Optional[str] = None
    dob: Optional[str] = None
    nationality: Optional[str] = None
    passport_no: Optional[str] = None
    # Contact info per passenger (Legacy requirement for request)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class BookingRequest(BaseBFFModel):
    offer_id: str
    passengers: List[PassengerRequest]
    contact_email: EmailStr
    contact_phone: Optional[str] = None

class BookingPassengerResponse(BaseBFFModel):
    pax_id: str
    title: Optional[str] = None
    first_name: str
    last_name: str
    name: Optional[str] = None
    dob: Optional[str] = None
    nationality: Optional[str] = None
    passport_no: Optional[str] = None
    type: str

class BookingContact(BaseBFFModel):
    email: EmailStr
    phone: Optional[str] = None

class BookingTicketing(BaseBFFModel):
    status: str
    time_limit: Optional[datetime] = None
    ticket_numbers: List[str] = []

class BookingResponse(BaseBFFModel):
    booking_reference: str
    pnr: str
    status: str
    status_code: str
    offer_id: str
    passengers: List[BookingPassengerResponse]
    contact: BookingContact
    ticketing: BookingTicketing
    created_at: datetime
