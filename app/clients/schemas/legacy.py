from pydantic import BaseModel, Field, ConfigDict
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

# --- Legacy Booking Response Schemas ---
class LegacyPassenger(BaseModel):
    pax_id: Optional[str] = None
    title: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="FirstName")
    last_name: Optional[str] = Field(None, alias="LastName")
    name: Optional[str] = None
    dob: Optional[str] = Field(None, alias="DateOfBirth")
    nationality: Optional[str] = None
    passport_no: Optional[str] = None
    type: Optional[str] = Field(None, alias="PaxType")

    model_config = ConfigDict(populate_by_name=True)

class LegacyContact(BaseModel):
    email: Optional[str] = Field(None, alias="EmailAddress")
    phone: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class LegacyTicketing(BaseModel):
    status: Optional[str] = None
    time_limit: Optional[str] = None
    ticket_numbers: List[str] = []

class LegacyBookingData(BaseModel):
    booking_ref: Optional[str] = Field(None, alias="BookingReference")
    pnr: Optional[str] = Field(None, alias="PNR")
    status: Optional[str] = None
    status_code: Optional[str] = Field(None, alias="StatusCode")
    offer_id: Optional[str] = None
    passengers: List[LegacyPassenger] = []
    contact: Optional[LegacyContact] = None
    ticketing: Optional[LegacyTicketing] = None
    created_at: Optional[str] = None
    created_date_time: Optional[int] = Field(None, alias="CreatedDateTime")

    model_config = ConfigDict(populate_by_name=True)

class LegacyBookingResponse(BaseModel):
    result: str = Field(alias="Result")
    result_code: int = Field(alias="ResultCode")
    data: LegacyBookingData
