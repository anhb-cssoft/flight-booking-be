import httpx
from typing import Any, Dict, List, Optional, Union
from app.core.config import settings
from app.clients.schemas import legacy as legacy_schemas
import logging

logger = logging.getLogger(__name__)

class LegacyAPIClient:
    def __init__(self, base_url: str = settings.LEGACY_API_BASE_URL, timeout: int = settings.LEGACY_API_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Handle inconsistent error formats
                try:
                    error_data = e.response.json()
                except:
                    error_data = e.response.text
                logger.error(f"Legacy API Error [{e.response.status_code}] at {url}: {error_data}")
                # We could raise custom exceptions here depending on the format
                # The user will likely handle these in the service layer
                raise e
            except Exception as e:
                logger.error(f"Error connecting to Legacy API at {url}: {str(e)}")
                raise e

    async def search_flights(self, request_data: legacy_schemas.SearchRequest) -> Dict[str, Any]:
        """POST /api/v1/flightsearch"""
        return await self._request("POST", "/api/v1/flightsearch", json=request_data.model_dump())

    async def get_offer_details(self, offer_id: str) -> Dict[str, Any]:
        """GET /api/v2/offer/{offer_id}"""
        return await self._request("GET", f"/api/v2/offer/{offer_id}")

    async def create_booking(self, request_data: legacy_schemas.CreateBookingRequest) -> Dict[str, Any]:
        """POST /booking/create (NOTE: No /api prefix)"""
        return await self._request("POST", "/booking/create", json=request_data.model_dump())

    async def get_reservation(self, ref: str) -> Dict[str, Any]:
        """GET /api/v1/reservations/{ref}"""
        return await self._request("GET", f"/api/v1/reservations/{ref}")

    async def list_airports(self) -> List[str]:
        """GET /api/airports"""
        return await self._request("GET", "/api/airports")

    async def get_airport(self, code: str) -> Dict[str, Any]:
        """GET /api/airports/{code}"""
        return await self._request("GET", f"/api/airports/{code}")

legacy_api_client = LegacyAPIClient()
