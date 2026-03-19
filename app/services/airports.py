import diskcache
from typing import List, Dict, Optional
from app.clients.legacy_api import legacy_api_client
from app.api.v1.schemas import flights as bff_schemas
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

class AirportService:
    def __init__(self):
        self.cache = diskcache.Cache(settings.CACHE_DIR)

    async def list_airports(self) -> List[bff_schemas.AirportInfo]:
        """List all airports with city names, using cache."""
        cache_key = "all_airports"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return [bff_schemas.AirportInfo(**item) for item in cached_result]

        # Fetch codes from legacy
        codes = await legacy_api_client.list_airports()
        
        # Fetch details for each code in parallel
        tasks = [self.get_airport(code) for code in codes]
        airports = await asyncio.gather(*tasks)
        
        # Store in cache
        self.cache.set(cache_key, [a.model_dump() for a in airports], expire=settings.AIRPORT_CACHE_TTL)
        
        return airports

    async def get_airport(self, code: str) -> bff_schemas.AirportInfo:
        """Get single airport info, using cache."""
        cache_key = f"airport_{code}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return bff_schemas.AirportInfo(**cached_result)

        try:
            legacy_data = await legacy_api_client.get_airport(code)
            airport = bff_schemas.AirportInfo(
                code=legacy_data.get("code", code),
                city=legacy_data.get("city")
            )
            self.cache.set(cache_key, airport.model_dump(), expire=settings.AIRPORT_CACHE_TTL)
            return airport
        except Exception as e:
            logger.error(f"Error fetching airport {code}: {str(e)}")
            return bff_schemas.AirportInfo(code=code, city=None)

airport_service = AirportService()
