from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re
import asyncio
from app.clients.legacy_api import legacy_api_client
from app.clients.schemas import legacy as legacy_schemas
from app.api.v1.schemas import flights as bff_schemas
from app.services.airports import airport_service

class FlightService:
    def _parse_legacy_datetime(self, dt_val: Union[str, int]) -> datetime:
        """Helper to parse the chaotic legacy datetime formats."""
        if isinstance(dt_val, int):
            return datetime.fromtimestamp(dt_val)
        
        if not isinstance(dt_val, str):
            return datetime.now() # Fallback

        # Try various formats
        formats = [
            "%Y%m%d%H%M%S",          # 20241225055000
            "%d/%m/%Y %H:%M",        # 25/12/2024 05:50
            "%d-%b-%Y %I:%M %p",     # 25-Dec-2024 01:10 PM
            "%Y-%m-%dT%H:%M:%S%z",   # 2024-12-25T12:10:00+07:00
            "%Y-%m-%d"               # 2024-12-25
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_val, fmt)
            except ValueError:
                continue
        
        # If it's a numeric string (timestamp)
        if dt_val.isdigit():
            return datetime.fromtimestamp(int(dt_val))
            
        return datetime.now() # Fallback

    async def _map_legacy_offer_to_bff(self, legacy_offer: Dict[str, Any]) -> bff_schemas.FlightOffer:
        segments = []
        legacy_segments = legacy_offer.get("segments", {}).get("segment_list", [])
        
        for leg_wrapper in legacy_segments:
            for leg in leg_wrapper.get("leg_data", []):
                dep_info = leg.get("departure_info", {})
                arr_info = leg.get("arrival_info", {})
                carrier = leg.get("carrier", {})
                
                origin_code = dep_info.get("airport", {}).get("code", "UNK")
                dest_code = arr_info.get("airport", {}).get("code", "UNK")
                
                # Fetch city names from cache (fast)
                origin_airport = await airport_service.get_airport(origin_code)
                dest_airport = await airport_service.get_airport(dest_code)
                
                # Use scheduled_time or dt for departure
                dep_time = self._parse_legacy_datetime(dep_info.get("scheduled_time") or dep_info.get("dt"))
                # Use scheduled_time or arr_date for arrival
                arr_time = self._parse_legacy_datetime(arr_info.get("scheduled_time") or arr_info.get("arr_date"))
                
                segments.append(bff_schemas.FlightSegment(
                    flight_number=carrier.get("number") or f"{carrier.get('operating')}{carrier.get('flight_no')}",
                    carrier=carrier.get("operating", "Unknown"),
                    origin=origin_code,
                    origin_city=origin_airport.city,
                    destination=dest_code,
                    destination_city=dest_airport.city,
                    departure_at=dep_time,
                    arrival_at=arr_time,
                    duration_minutes=leg.get("duration_minutes", 0)
                ))
        
        pricing = legacy_offer.get("pricing", {})
        
        return bff_schemas.FlightOffer(
            offer_id=legacy_offer.get("offer_id"),
            total_price=float(pricing.get("total", 0)),
            currency=pricing.get("currency", "USD"),
            segments=segments,
            is_refundable=legacy_offer.get("refundable", False),
            cabin_class=legacy_offer.get("cabin_class", "ECONOMY")
        )

    async def search_flights(self, search_req: bff_schemas.FlightSearchRequest) -> bff_schemas.FlightSearchResponse:
        # Mapping BFF cabin classes to Legacy codes: ECONOMY -> Y, etc.
        cabin_map = {
            "ECONOMY": "Y",
            "PREMIUM_ECONOMY": "W",
            "BUSINESS": "J",
            "FIRST": "F"
        }
        # Use .upper() to handle cases like "economy"
        legacy_cabin = cabin_map.get(search_req.cabin.upper(), "Y")

        legacy_req = legacy_schemas.SearchRequest(
            origin=search_req.origin,
            destination=search_req.destination,
            departure_date=search_req.departure_date,
            return_date=search_req.return_date,
            pax_count=search_req.passengers,
            cabin=legacy_cabin
        )
        
        legacy_data = await legacy_api_client.search_flights(legacy_req)
        
        flight_results = legacy_data.get("data", {}).get("flight_results", {})
        
        # Process Outbound
        outbound_data = flight_results.get("outbound", {}).get("results", [])
        outbound_tasks = [self._map_legacy_offer_to_bff(offer) for offer in outbound_data]
        outbound_offers = await asyncio.gather(*outbound_tasks)
        
        # Process Inbound (if return trip)
        inbound_data = flight_results.get("inbound", {}).get("results", [])
        inbound_tasks = [self._map_legacy_offer_to_bff(offer) for offer in inbound_data]
        inbound_offers = await asyncio.gather(*inbound_tasks)
        
        return bff_schemas.FlightSearchResponse(
            outbound_count=len(outbound_offers),
            outbound_offers=outbound_offers,
            inbound_count=len(inbound_offers),
            inbound_offers=inbound_offers
        )

    async def get_offer_details(self, offer_id: str) -> bff_schemas.FlightOffer:
        legacy_data = await legacy_api_client.get_offer_details(offer_id)
        return await self._map_legacy_offer_to_bff(legacy_data)

flight_service = FlightService()
