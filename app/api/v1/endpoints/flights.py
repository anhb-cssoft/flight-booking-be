from fastapi import APIRouter, HTTPException
from app.api.v1.schemas import flights as bff_schemas
from app.services.flights import flight_service

router = APIRouter()

@router.post("/search", response_model=bff_schemas.FlightSearchResponse)
async def search_flights(request: bff_schemas.FlightSearchRequest):
    try:
        return await flight_service.search_flights(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching flights: {str(e)}")

@router.get("/offers/{offer_id}", response_model=bff_schemas.FlightOfferDetails)
async def get_offer_details(offer_id: str):
    try:
        return await flight_service.get_offer_details(offer_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Offer not found: {str(e)}")
