import diskcache
from typing import List, Dict, Optional
from app.clients.legacy_api import legacy_api_client
from app.api.v1.schemas import flights as bff_schemas
from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError
import asyncio
import logging

logger = logging.getLogger(__name__)

class AirportService:
    def __init__(self):
        self.cache = diskcache.Cache(settings.CACHE_DIR)
        # Limit parallel calls during simulation to prevent overwhelming legacy or BFF
        self._semaphore = asyncio.Semaphore(10)

    async def list_airports(self, simulate_issues: Optional[bool] = None) -> List[bff_schemas.AirportInfo]:
        """List all airports with city names, using cache."""
        cache_key = "all_airports"
        if not simulate_issues:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return [bff_schemas.AirportInfo(**item) for item in cached_result]

        # Fetch codes from legacy
        codes = await legacy_api_client.list_airports(simulate_issues=simulate_issues)
        
        # Limit to first 20 for faster demo if simulating issues
        if simulate_issues and len(codes) > 20:
            logger.info(f"Simulating issues: Limiting to 20/ {len(codes)} airports for faster feedback.")
            codes = codes[:20]

        # Fetch details for each code with semaphore control
        async def fetch_with_semaphore(code):
            async with self._semaphore:
                return await self.get_airport(code, simulate_issues=simulate_issues)

        tasks = [fetch_with_semaphore(code) for code in codes]
        airports = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for airport in airports:
            if isinstance(airport, bff_schemas.AirportInfo):
                results.append(airport)
            elif isinstance(airport, Exception):
                # If we hit a serious error (like Circuit Breaker Open), stop and raise
                if "Circuit Breaker OPEN" in str(airport):
                    raise airport

        # Store in cache only if not simulating issues
        if not simulate_issues and results:
            self.cache.set(cache_key, [a.model_dump() for a in results], expire=settings.AIRPORT_CACHE_TTL)
        
        return results

    async def get_airport(self, code: str, simulate_issues: Optional[bool] = None) -> bff_schemas.AirportInfo:
        """Get single airport info, using cache."""
        cache_key = f"airport_{code}"
        if not simulate_issues:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return bff_schemas.AirportInfo(**cached_result)

        try:
            legacy_data = await legacy_api_client.get_airport(code, simulate_issues=simulate_issues)
            airport = bff_schemas.AirportInfo(
                code=legacy_data.get("code", code),
                city=legacy_data.get("city")
            )
            if not simulate_issues:
                self.cache.set(cache_key, airport.model_dump(), expire=settings.AIRPORT_CACHE_TTL)
            return airport
        except Exception as e:
            logger.error(f"Error fetching airport {code}: {str(e)}")
            # If it's a circuit breaker or rate limit, re-raise to be handled by list_airports
            if "Circuit Breaker" in str(e) or "429" in str(e):
                raise e
            return bff_schemas.AirportInfo(code=code, city=None)

airport_service = AirportService()
