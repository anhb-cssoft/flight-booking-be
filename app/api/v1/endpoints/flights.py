from typing import Optional
from fastapi import APIRouter
from app.api.v1.schemas import flights as bff_schemas
from app.services.flights import flight_service

router = APIRouter()

@router.post("/search", response_model=bff_schemas.FlightSearchResponse)
async def search_flights(request: bff_schemas.FlightSearchRequest, simulate_issues: Optional[bool] = None):
    return await flight_service.search_flights(request, simulate_issues=simulate_issues)

@router.get("/offers/{offer_id}", response_model=bff_schemas.FlightOfferDetails)
async def get_offer_details(offer_id: str, simulate_issues: Optional[bool] = None):
    return await flight_service.get_offer_details(offer_id, simulate_issues=simulate_issues)
