from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AirportInfo(BaseModel):
    code: str
    city: Optional[str] = None

class FlightSegment(BaseModel):
    flight_number: str
    carrier: str
    origin: str
    origin_city: Optional[str] = None
    destination: str
    destination_city: Optional[str] = None
    departure_at: datetime
    arrival_at: datetime
    duration_minutes: int

class FlightOffer(BaseModel):
    offer_id: str
    total_price: float
    currency: str = "USD"
    segments: List[FlightSegment]
    is_refundable: bool = True
    cabin_class: str

class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    cabin: str = "Y"

class FlightSearchResponse(BaseModel):
    outbound_count: int
    outbound_offers: List[FlightOffer]
    inbound_count: int = 0
    inbound_offers: List[FlightOffer] = []
