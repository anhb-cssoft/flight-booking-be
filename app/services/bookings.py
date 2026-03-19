from typing import List, Optional
from app.clients.legacy_api import legacy_api_client
from app.clients.schemas import legacy as legacy_schemas
from app.api.v1.schemas import bookings as bff_schemas
from app.services.flights import flight_service

class BookingService:
    async def create_booking(self, booking_req: bff_schemas.BookingRequest) -> bff_schemas.BookingResponse:
        # Map BFF request to Legacy request
        legacy_passengers = [
            legacy_schemas.BookingPassenger(
                first_name=p.first_name,
                last_name=p.last_name,
                title=p.title,
                email=str(p.email) if p.email else None,
                phone=p.phone,
                passport_no=p.passport_no
            ) for p in booking_req.passengers
        ]
        
        legacy_req = legacy_schemas.CreateBookingRequest(
            offer_id=booking_req.offer_id,
            passengers=legacy_passengers,
            contact_email=str(booking_req.contact_email),
            contact_phone=booking_req.contact_phone
        )
        
        legacy_res = await legacy_api_client.create_booking(legacy_req)
        
        # Robustly extract booking reference and status from legacy response
        # The legacy response often nests data in a 'data' node and uses varying key names
        res_data = legacy_res.get("data", {}) if isinstance(legacy_res.get("data"), dict) else legacy_res
        
        booking_ref = (
            res_data.get("booking_ref") or 
            res_data.get("booking_reference") or 
            res_data.get("BookingReference") or 
            res_data.get("pnr") or 
            res_data.get("PNR") or 
            "FAILED"
        )
        
        status = res_data.get("status") or res_data.get("StatusCode") or "CONFIRMED"
        
        return bff_schemas.BookingResponse(
            booking_reference=booking_ref,
            status=status,
            total_price=0.0, # Placeholder or extract from legacy_res if available
            currency="USD", # Placeholder or extract from legacy_res if available
            passengers=booking_req.passengers,
            offer_details=None
        )

    async def get_booking(self, ref: str) -> bff_schemas.BookingResponse:
        legacy_res = await legacy_api_client.get_reservation(ref)
        # Map legacy reservation to BFF response
        # This would need more mapping logic based on actual response
        return bff_schemas.BookingResponse(
            booking_reference=ref,
            status=legacy_res.get("status", "OK"),
            total_price=0.0, # Would need to extract from legacy_res
            currency="USD",
            passengers=[], # Would need to extract from legacy_res
            offer_details=None
        )

booking_service = BookingService()
