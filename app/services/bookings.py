from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.clients.legacy_api import legacy_api_client
from app.clients.schemas import legacy as legacy_schemas
from app.api.v1.schemas import bookings as bff_schemas

class BookingService:
    def _parse_legacy_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str or len(date_str) != 14:
            return None
        try:
            return datetime.strptime(date_str, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def _map_legacy_to_bff(self, legacy_res: Dict[str, Any]) -> bff_schemas.BookingResponse:
        # In a real scenario, we'd parse this into LegacyBookingResponse model
        data_dict = legacy_res.get("data", {}) if isinstance(legacy_res.get("data"), dict) else legacy_res
        
        # Transform data to BFF structure
        passengers = [
            bff_schemas.BookingPassengerResponse(
                pax_id=p.get("pax_id"),
                title=p.get("title"),
                first_name=p.get("first_name") or p.get("FirstName") or "",
                last_name=p.get("last_name") or p.get("LastName") or "",
                name=p.get("name"),
                dob=p.get("dob") or p.get("DateOfBirth"),
                nationality=p.get("nationality"),
                passport_no=p.get("passport_no"),
                type=p.get("type") or p.get("PaxType") or "ADT"
            ) for p in data_dict.get("passengers", [])
        ]
        
        contact_raw = data_dict.get("contact", {})
        contact = bff_schemas.BookingContact(
            email=contact_raw.get("email") or contact_raw.get("EmailAddress") or "unknown@email.com",
            phone=contact_raw.get("phone")
        )
        
        ticketing_raw = data_dict.get("ticketing", {})
        ticketing = bff_schemas.BookingTicketing(
            status=ticketing_raw.get("status") or "PENDING",
            time_limit=self._parse_legacy_date(ticketing_raw.get("time_limit")),
            ticket_numbers=ticketing_raw.get("ticket_numbers", [])
        )
        
        created_at = self._parse_legacy_date(data_dict.get("created_at"))
        if not created_at and data_dict.get("CreatedDateTime"):
            created_at = datetime.fromtimestamp(data_dict.get("CreatedDateTime"), tz=timezone.utc)

        return bff_schemas.BookingResponse(
            booking_reference=data_dict.get("booking_ref") or data_dict.get("BookingReference") or "N/A",
            pnr=data_dict.get("pnr") or data_dict.get("PNR") or "N/A",
            status=data_dict.get("status") or "UNKNOWN",
            status_code=data_dict.get("StatusCode") or "XX",
            offer_id=data_dict.get("offer_id") or "N/A",
            passengers=passengers,
            contact=contact,
            ticketing=ticketing,
            created_at=created_at or datetime.now(timezone.utc)
        )

    async def create_booking(self, booking_req: bff_schemas.BookingRequest) -> bff_schemas.BookingResponse:
        # Map BFF request to Legacy request
        legacy_passengers = [
            legacy_schemas.BookingPassenger(
                first_name=p.first_name,
                last_name=p.last_name,
                title=p.title,
                dob=p.dob,
                nationality=p.nationality,
                passport_no=p.passport_no,
                email=str(p.email) if p.email else None,
                phone=p.phone
            ) for p in booking_req.passengers
        ]
        
        legacy_req = legacy_schemas.CreateBookingRequest(
            offer_id=booking_req.offer_id,
            passengers=legacy_passengers,
            contact_email=str(booking_req.contact_email),
            contact_phone=booking_req.contact_phone
        )
        
        legacy_res = await legacy_api_client.create_booking(legacy_req)
        return self._map_legacy_to_bff(legacy_res)

    async def get_booking(self, ref: str) -> bff_schemas.BookingResponse:
        legacy_res = await legacy_api_client.get_reservation(ref)
        return self._map_legacy_to_bff(legacy_res)

booking_service = BookingService()
