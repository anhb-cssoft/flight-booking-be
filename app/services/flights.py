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
        """Helper to parse the chaotic legacy datetime formats into ISO 8601 compliant objects."""
        if not dt_val:
            return datetime.now()

        if isinstance(dt_val, int):
            return datetime.fromtimestamp(dt_val)
        
        if not isinstance(dt_val, str):
            return datetime.now()

        # Clean string from common artifacts
        dt_val = dt_val.strip()

        # Try various formats
        formats = [
            "%Y%m%d%H%M%S",          # 20241225055000
            "%d/%m/%Y %H:%M",        # 25/12/2024 05:50
            "%d-%b-%Y %I:%M %p",     # 25-Dec-2024 01:10 PM
            "%Y-%m-%dT%H:%M:%S%z",   # 2024-12-25T12:10:00+07:00
            "%Y-%m-%dT%H:%M:%S",     # 2024-12-25T12:10:00
            "%d/%m/%Y",              # 25/12/2024
            "%Y-%m-%d",              # 2024-12-25
            "%d-%b-%Y %H:%M",        # 25-Dec-2024 13:10
            "%d-%m-%Y %I:%M %p",     # 19-Dec-2024 09:40 PM
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_val, fmt)
            except ValueError:
                continue
        
        # If it's a numeric string (timestamp)
        if dt_val.isdigit():
            if len(dt_val) == 14: # YYYYMMDDHHmmss
                try:
                    return datetime.strptime(dt_val, "%Y%m%d%H%M%S")
                except:
                    pass
            try:
                return datetime.fromtimestamp(int(dt_val))
            except:
                pass
            
        return datetime.now()

    async def _map_legacy_offer_to_bff(self, legacy_offer: Dict[str, Any], context: str = "search") -> Union[bff_schemas.FlightSearchOffer, bff_schemas.FlightOfferDetails]:
        segments = []
        legacy_segments = legacy_offer.get("segments", {}).get("segment_list", [])
        
        detected_cabin_code = None
        for leg_wrapper in legacy_segments:
            for leg in leg_wrapper.get("leg_data", []):
                dep_info = leg.get("departure_info", {})
                arr_info = leg.get("arrival_info", {})
                carrier = leg.get("carrier", {})
                
                if not detected_cabin_code:
                    detected_cabin_code = leg.get("cabin") or leg.get("cabin_class")

                origin_code = dep_info.get("airport", {}).get("code", "UNK")
                dest_code = arr_info.get("airport", {}).get("code", "UNK")
                
                origin_airport = await airport_service.get_airport(origin_code)
                dest_airport = await airport_service.get_airport(dest_code)
                
                dep_time = self._parse_legacy_datetime(dep_info.get("scheduled_time") or dep_info.get("dt"))
                arr_time = self._parse_legacy_datetime(arr_info.get("scheduled_time") or arr_info.get("arr_date"))
                
                segments.append(bff_schemas.FlightSegment(
                    flight_number=carrier.get("number") or f"{carrier.get('operating')}{carrier.get('flight_no')}",
                    carrier=carrier.get("operating", "Unknown"),
                    origin=origin_code,
                    origin_city=origin_airport.city,
                    origin_terminal=dep_info.get("airport", {}).get("terminal"),
                    destination=dest_code,
                    destination_city=dest_airport.city,
                    destination_terminal=arr_info.get("airport", {}).get("terminal"),
                    departure_at=dep_time,
                    arrival_at=arr_time,
                    duration_minutes=leg.get("duration_minutes", 0),
                    aircraft_code=leg.get("equipment", {}).get("aircraft_code") or leg.get("equipment", {}).get("type")
                ))
        
        # Cabin mapping
        cabin_code = legacy_offer.get("cabin_class") or legacy_offer.get("booking_class") or detected_cabin_code
        final_cabin_label = "ECONOMY"
        if cabin_code:
            cabin_reverse_map = {"Y": "ECONOMY", "W": "PREMIUM_ECONOMY", "J": "BUSINESS", "C": "BUSINESS", "F": "FIRST"}
            final_cabin_label = cabin_reverse_map.get(str(cabin_code).upper(), "ECONOMY")

        # Pricing mapping
        legacy_pricing = legacy_offer.get("pricing", {})
        taxes_fees = legacy_pricing.get("taxes_fees", {})
        pricing = bff_schemas.PricingBreakdown(
            total=float(legacy_pricing.get("total") or legacy_pricing.get("total_amount") or 0),
            base=float(legacy_pricing.get("base_fare") or legacy_pricing.get("BaseFare") or 0),
            tax=float(taxes_fees.get("total_tax") or taxes_fees.get("TotalTax") or 0),
            currency=legacy_pricing.get("currency") or legacy_pricing.get("CurrencyCode") or "USD",
            tax_breakdown=[
                bff_schemas.TaxItem(code=t.get("code"), amount=float(t.get("amount") or 0))
                for t in taxes_fees.get("tax_breakdown", [])
            ]
        )

        # Baggage mapping
        legacy_baggage = legacy_offer.get("baggage", {}) or legacy_offer.get("baggage_allowance", {})
        baggage = bff_schemas.BaggageAllowance(
            checked_pieces=legacy_baggage.get("checked", {}).get("pieces"),
            checked_weight_kg=legacy_baggage.get("checked", {}).get("weight_kg") or legacy_baggage.get("checked", {}).get("max_weight_kg"),
            cabin_pieces=legacy_baggage.get("cabin_baggage", {}).get("pieces") or legacy_baggage.get("carry_on", {}).get("pieces"),
            cabin_weight_kg=legacy_baggage.get("cabin_baggage", {}).get("weight_kg") or legacy_baggage.get("carry_on", {}).get("max_weight_kg")
        )

        common_data = {
            "offer_id": legacy_offer.get("offer_id") or legacy_offer.get("id") or legacy_offer.get("offerId"),
            "segments": segments,
            "is_refundable": legacy_offer.get("refundable") if legacy_offer.get("refundable") is not None else legacy_offer.get("isRefundable", True),
            "cabin_class": final_cabin_label,
            "pricing": pricing,
            "baggage": baggage,
            "seats_remaining": legacy_offer.get("seats_remaining") or legacy_offer.get("avl_seats") or legacy_offer.get("seatAvailability"),
            "fare_basis": legacy_offer.get("fare_basis"),
            "booking_class": legacy_offer.get("booking_class"),
            "validating_carrier": legacy_offer.get("validating_carrier")
        }

        if context == "search":
            return bff_schemas.FlightSearchOffer(**common_data)
        
        # Details context
        status = legacy_offer.get("status")
        expires_at_raw = legacy_offer.get("expires_at") or legacy_offer.get("last_ticketing_date")
        expires_at = self._parse_legacy_datetime(expires_at_raw) if expires_at_raw else None
        
        time_limit_raw = legacy_offer.get("payment_requirements", {}).get("time_limit")
        time_limit = self._parse_legacy_datetime(time_limit_raw) if time_limit_raw else None

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
                currency=refund.get("penalty", {}).get("currency") or pricing.currency
            )

        return bff_schemas.FlightOfferDetails(
            **common_data,
            status=status,
            expires_at=expires_at,
            time_limit=time_limit,
            fare_rules=fare_rules
        )

    async def search_flights(self, search_req: bff_schemas.FlightSearchRequest) -> bff_schemas.FlightSearchResponse:
        cabin_map = {"ECONOMY": "Y", "PREMIUM_ECONOMY": "W", "BUSINESS": "J", "FIRST": "F", "Y": "Y", "W": "W", "J": "J", "F": "F"}
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
        
        outbound_data = flight_results.get("outbound", {}).get("results", [])
        outbound_tasks = [self._map_legacy_offer_to_bff(offer, context="search") for offer in outbound_data]
        outbound_offers = await asyncio.gather(*outbound_tasks)
        
        inbound_data = flight_results.get("inbound", {}).get("results", [])
        inbound_tasks = [self._map_legacy_offer_to_bff(offer, context="search") for offer in inbound_data]
        inbound_offers = await asyncio.gather(*inbound_tasks)
        
        return bff_schemas.FlightSearchResponse(
            outbound_count=len(outbound_offers),
            outbound_offers=outbound_offers,
            inbound_count=len(inbound_offers),
            inbound_offers=inbound_offers
        )

    async def get_offer_details(self, offer_id: str) -> bff_schemas.FlightOfferDetails:
        legacy_data = await legacy_api_client.get_offer_details(offer_id)
        offer_node = legacy_data.get("data", {}).get("offer", {})
        if not offer_node:
            offer_node = legacy_data.get("offer", {}) or legacy_data
            
        return await self._map_legacy_offer_to_bff(offer_node, context="details")

flight_service = FlightService()
