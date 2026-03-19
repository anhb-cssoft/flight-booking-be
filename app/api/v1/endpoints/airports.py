from typing import List, Optional
from fastapi import APIRouter
from app.api.v1.schemas import flights as bff_schemas
from app.services.airports import airport_service

router = APIRouter()

@router.get("", response_model=List[bff_schemas.AirportInfo])
async def list_airports(simulate_issues: Optional[bool] = None):
    return await airport_service.list_airports(simulate_issues=simulate_issues)

@router.get("/{code}", response_model=bff_schemas.AirportInfo)
async def get_airport(code: str, simulate_issues: Optional[bool] = None):
    return await airport_service.get_airport(code, simulate_issues=simulate_issues)
