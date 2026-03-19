from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Optional
from datetime import datetime

class BaseBFFModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

class AirportInfo(BaseBFFModel):
    code: str
    city: Optional[str] = None

class FlightSegment(BaseBFFModel):
    flight_number: str
    carrier: str
    origin: str
    origin_city: Optional[str] = None
    origin_terminal: Optional[str] = None
    destination: str
    destination_city: Optional[str] = None
    destination_terminal: Optional[str] = None
    departure_at: datetime
    arrival_at: datetime
    duration_minutes: int
    aircraft_code: Optional[str] = None

class FareRules(BaseBFFModel):
    refund_allowed: bool
    refund_penalty: Optional[float] = None
    change_allowed: bool
    change_penalty: Optional[float] = None
    currency: Optional[str] = "USD"

class TaxItem(BaseBFFModel):
    code: str
    amount: float

class PricingBreakdown(BaseBFFModel):
    total: float
    base: float
    tax: float
    currency: str = "USD"
    tax_breakdown: List[TaxItem] = []

class BaggageAllowance(BaseBFFModel):
    checked_pieces: Optional[int] = None
    checked_weight_kg: Optional[int] = None
    cabin_pieces: Optional[int] = None
    cabin_weight_kg: Optional[int] = None

# Base class for common fields
class FlightOfferBase(BaseBFFModel):
    offer_id: str
    is_refundable: bool = True
    cabin_class: Optional[str] = None

# Lean model for Search Results
class FlightSearchOffer(FlightOfferBase):
    segments: List[FlightSegment] = []
    pricing: PricingBreakdown
    baggage: Optional[BaggageAllowance] = None
    seats_remaining: Optional[int] = None
    fare_basis: Optional[str] = None
    booking_class: Optional[str] = None
    validating_carrier: Optional[str] = None

# New detailed models for v2 Offer Details
class FarePenalty(BaseBFFModel):
    amount: float
    currency: str = "USD"

class DetailedFareRules(BaseBFFModel):
    refund: Optional[dict] = None # {allowed: bool, penalty: FarePenalty}
    change: Optional[dict] = None # {allowed: bool, penalty: FarePenalty}
    no_show: Optional[dict] = None # {penalty: FarePenalty}

class BaggageDetail(BaseBFFModel):
    quantity: Optional[int] = None
    weight_kg: Optional[int] = None

class DetailedBaggageAllowance(BaseBFFModel):
    checked: Optional[BaggageDetail] = None
    cabin: Optional[BaggageDetail] = None

class FareConditions(BaseBFFModel):
    advance_purchase_days: Optional[int] = None
    min_stay_days: Optional[int] = None
    max_stay_days: Optional[int] = None

class PaymentRequirements(BaseBFFModel):
    accepted_methods: List[str] = []
    time_limit: Optional[datetime] = None
    instant_ticketing_required: bool = False

# Enriched model for Offer Details (v2) - Strict mapping
class FlightOfferDetails(FlightOfferBase):
    status: Optional[str] = None
    fare_family: Optional[str] = None
    pricing: Optional[PricingBreakdown] = None
    rules: Optional[DetailedFareRules] = None
    conditions: Optional[FareConditions] = None
    baggage_allowance: Optional[DetailedBaggageAllowance] = None
    payment_requirements: Optional[PaymentRequirements] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class FlightSearchRequest(BaseBFFModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    cabin: str = "Y"

class FlightSearchResponse(BaseBFFModel):
    outbound_count: int
    outbound_offers: List[FlightSearchOffer]
    inbound_count: int = 0
    inbound_offers: List[FlightSearchOffer] = []
