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
            "%Y%m%d%H%M%S",          # 20241225055000 / 20260319082124
            "%d/%m/%Y %H:%M",        # 25/12/2024 05:50 / 20/03/2026 08:46
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
            # Handle long timestamp string
            if len(dt_val) > 10:
                try:
                    return datetime.strptime(dt_val, "%Y%m%d%H%M%S")
                except:
                    pass
            return datetime.fromtimestamp(int(dt_val))
            
        return datetime.now() # Fallback

    async def _map_legacy_offer_to_bff(self, legacy_offer: Dict[str, Any]) -> bff_schemas.FlightOffer:
        segments = []
        legacy_segments = legacy_offer.get("segments", {}).get("segment_list", [])
        
        # Track cabin code from segments to use as fallback
        detected_cabin_code = None
        
        for leg_wrapper in legacy_segments:
            for leg in leg_wrapper.get("leg_data", []):
                dep_info = leg.get("departure_info", {})
                arr_info = leg.get("arrival_info", {})
                carrier = leg.get("carrier", {})
                
                # Capture cabin code (e.g., 'Y', 'W')
                if not detected_cabin_code:
                    detected_cabin_code = leg.get("cabin") or leg.get("cabin_class")

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
        
        # Cabin logic
        cabin_code = legacy_offer.get("cabin_class") or legacy_offer.get("booking_class") or detected_cabin_code
        final_cabin_label = None
        if cabin_code:
            cabin_reverse_map = {
                "Y": "ECONOMY",
                "W": "PREMIUM_ECONOMY",
                "J": "BUSINESS",
                "F": "FIRST"
            }
            final_cabin_label = cabin_reverse_map.get(cabin_code.upper(), "ECONOMY")

        # Fare Rules logic (Enrichment)
        fare_details = legacy_offer.get("fare_details", {})
        rules = fare_details.get("rules", {})
        refund = rules.get("refund", {})
        change = rules.get("change", {})
        
        fare_rules = None
        if rules:
            fare_rules = bff_schemas.FareRules(
                refund_allowed=refund.get("allowed", True),
                refund_penalty=refund.get("penalty", {}).get("amount"),
                change_allowed=change.get("allowed", True),
                change_penalty=change.get("penalty", {}).get("amount"),
                currency=refund.get("penalty", {}).get("currency") or "USD"
            )

        # Baggage logic (Enrichment)
        baggage_data = legacy_offer.get("baggage_allowance", {})
        baggage = None
        if baggage_data:
            baggage = bff_schemas.BaggageAllowance(
                checked_kg=baggage_data.get("checked", {}).get("max_weight_kg"),
                carry_on_kg=baggage_data.get("carry_on", {}).get("max_weight_kg")
            )
            
        # Extra details from /v2/offer
        expires_at_raw = legacy_offer.get("expires_at")
        expires_at = self._parse_legacy_datetime(expires_at_raw) if expires_at_raw else None
        
        time_limit_raw = legacy_offer.get("payment_requirements", {}).get("time_limit")
        time_limit = self._parse_legacy_datetime(time_limit_raw) if time_limit_raw else None

        return bff_schemas.FlightOffer(
            offer_id=legacy_offer.get("offer_id") or legacy_offer.get("id"),
            total_price=float(pricing.get("total")) if pricing and pricing.get("total") else 0.0,
            currency=pricing.get("currency", "USD") if pricing else "USD",
            segments=segments,
            is_refundable=legacy_offer.get("refundable", refund.get("allowed", True)),
            cabin_class=final_cabin_label,
            status=legacy_offer.get("status"),
            expires_at=expires_at,
            time_limit=time_limit,
            fare_rules=fare_rules,
            baggage=baggage
        )

    async def search_flights(self, search_req: bff_schemas.FlightSearchRequest) -> bff_schemas.FlightSearchResponse:
        # Mapping BFF cabin classes or codes to Legacy codes
        cabin_map = {
            "ECONOMY": "Y",
            "PREMIUM_ECONOMY": "W",
            "BUSINESS": "J",
            "FIRST": "F",
            "Y": "Y",
            "W": "W",
            "J": "J",
            "F": "F"
        }
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
        # Extract correctly from legacy nesting
        offer_node = legacy_data.get("data", {}).get("offer", {})
        if not offer_node:
            # Fallback if the nesting is different
            offer_node = legacy_data.get("offer", {}) or legacy_data
            
        return await self._map_legacy_offer_to_bff(offer_node)

flight_service = FlightService()
