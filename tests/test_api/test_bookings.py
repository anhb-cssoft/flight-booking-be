from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_booking_success():
    # Mocking the legacy API create booking response using the raw data example
    mock_legacy_booking = {
        "Result": "SUCCESS",
        "ResultCode": 0,
        "data": {
            "booking_ref": "EG12FA2A",
            "pnr": "B96170E",
            "status": "CONFIRMED",
            "StatusCode": "HK",
            "offer_id": "93f1d242d6fddd80",
            "passengers": [
                {
                    "pax_id": "PAX1",
                    "title": "Mr",
                    "first_name": "John",
                    "last_name": "Doe",
                    "name": "Doe/John Mr",
                    "dob": "1990-01-01",
                    "nationality": "US",
                    "passport_no": "123456789",
                    "type": "ADT"
                }
            ],
            "contact": {
                "email": "testuser@gmail.com",
                "phone": "1234567890"
            },
            "ticketing": {
                "status": "PENDING",
                "time_limit": "20260321060731",
                "ticket_numbers": []
            },
            "created_at": "20260319110731"
        }
    }

    with patch("app.clients.legacy_api.legacy_api_client.create_booking", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_legacy_booking

        response = client.post(
            "/api/v1/bookings",
            json={
                "offerId": "93f1d242d6fddd80",
                "passengers": [
                    {
                        "firstName": "John",
                        "lastName": "Doe",
                        "title": "Mr",
                        "dob": "1990-01-01",
                        "nationality": "US",
                        "passportNo": "123456789",
                        "email": "testuser@gmail.com",
                        "phone": "1234567890"
                    }
                ],
                "contactEmail": "testuser@gmail.com",
                "contactPhone": "1234567890"
            }
        )

        assert response.status_code == 200
        data = response.json()
        
        assert data["bookingReference"] == "EG12FA2A"
        assert data["pnr"] == "B96170E"
        assert data["status"] == "CONFIRMED"
        assert data["statusCode"] == "HK"
        assert "totalPrice" not in data
        assert "currency" not in data
        
        # Verify passengers
        assert len(data["passengers"]) == 1
        pax = data["passengers"][0]
        assert pax["paxId"] == "PAX1"
        assert pax["firstName"] == "John"
        assert pax["type"] == "ADT"
        
        # Verify contact
        assert data["contact"]["email"] == "testuser@gmail.com"
        
        # Verify ticketing
        assert data["ticketing"]["status"] == "PENDING"
        assert data["ticketing"]["timeLimit"] == "2026-03-21T06:07:31Z" # ISO format from datetime
        
        # Verify timestamps
        assert data["createdAt"] == "2026-03-19T11:07:31Z"
