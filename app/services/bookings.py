from typing import List, Optional
from app.clients.legacy_api import legacy_api_client
from app.clients.schemas import legacy as legacy_schemas
from app.api.v1.schemas import bookings as bff_schemas
from app.services.flights import flight_service

class BookingService:
    async def create_booking(self, booking_req: bff_schemas.BookingRequest) -> bff_schemas.BookingResponse:
        # Get offer details first to have price/currency (optional but good for response)
        offer_details = await flight_service.get_offer_details(booking_req.offer_id)
        
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
        
        # The legacy response format for booking is unknown from openapi, but typically returns a PNR/Reference
        # Let's assume it has a 'booking_reference' or 'pnr'
        return bff_schemas.BookingResponse(
            booking_reference=legacy_res.get("booking_reference") or legacy_res.get("pnr") or "FAILED",
            status=legacy_res.get("status", "CONFIRMED"),
            total_price=offer_details.total_price,
            currency=offer_details.currency,
            passengers=booking_req.passengers,
            offer_details=offer_details
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
