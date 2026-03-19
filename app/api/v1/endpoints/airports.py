from fastapi import APIRouter, HTTPException
from typing import List
from app.api.v1.schemas import flights as bff_schemas
from app.services.airports import airport_service

router = APIRouter()

@router.get("", response_model=List[bff_schemas.AirportInfo])
async def list_airports():
    try:
        return await airport_service.list_airports()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing airports: {str(e)}")

@router.get("/{code}", response_model=bff_schemas.AirportInfo)
async def get_airport(code: str):
    try:
        return await airport_service.get_airport(code)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Airport not found: {str(e)}")
