from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union

# --- Legacy Search Flight Schemas ---
class SearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    pax_count: int = 1
    cabin: str = "Y"

# --- Legacy Booking Passenger Schemas ---
class BookingPassenger(BaseModel):
    title: Optional[str] = None
    first_name: str
    last_name: str
    dob: Optional[str] = None
    nationality: Optional[str] = None
    passport_no: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

# --- Legacy Create Booking Schemas ---
class CreateBookingRequest(BaseModel):
    offer_id: str
    passengers: List[BookingPassenger]
    contact_email: str
    contact_phone: Optional[str] = None

# --- Legacy Airport Schemas ---
class LegacyAirport(BaseModel):
    code: str
    city: Optional[str] = None

# --- Legacy ValidationError Schemas ---
class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None
