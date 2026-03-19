from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_booking_success():
    # Mocking the legacy API create booking response
    mock_legacy_booking = {
        "Result": "SUCCESS",
        "data": {
            "booking_ref": "PNR123",
            "status": "CONFIRMED"
        }
    }

    with patch("app.clients.legacy_api.legacy_api_client.create_booking", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_legacy_booking

        response = client.post(
            "/api/v1/bookings",
            json={
                "offerId": "test_offer_id",
                "passengers": [
                    {
                        "firstName": "John",
                        "lastName": "Doe",
                        "title": "MR",
                        "email": "john.doe@example.com",
                        "phone": "+123456789",
                        "passportNo": "ABC123456"
                    }
                ],
                "contactEmail": "john.doe@example.com",
                "contactPhone": "+123456789"
            }
        )

        assert response.status_code == 200
        data = response.json()
        
        assert data["bookingReference"] == "PNR123"
        assert data["status"] == "CONFIRMED"
        # totalPrice and currency will be defaults as we removed offer_details call
        assert data["totalPrice"] == 0.0
        assert data["currency"] == "USD"
        assert data["offerDetails"] is None
