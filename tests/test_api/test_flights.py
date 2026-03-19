from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@pytest.mark.asyncio
async def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Flight Booking BFF is running"}

@pytest.mark.asyncio
async def test_search_flights():
    # Mocking the legacy API search response
    mock_response = {
        "data": {
            "flight_results": {
                "outbound": {
                    "results": [
                        {
                            "offer_id": "test_offer_1",
                            "segments": {
                                "segment_list": [
                                    {
                                        "leg_data": [
                                            {
                                                "departure_info": {
                                                    "airport": {"code": "HAN"},
                                                    "scheduled_time": "20241225055000"
                                                },
                                                "arrival_info": {
                                                    "airport": {"code": "SGN"},
                                                    "scheduled_time": "20241225080000"
                                                },
                                                "carrier": {"operating": "VN", "number": "VN123"},
                                                "duration_minutes": 130
                                            }
                                        ]
                                    }
                                ]
                            },
                            "pricing": {"total": 150.0, "currency": "USD"},
                            "refundable": True,
                            "cabin_class": "Y"
                        }
                    ]
                }
            }
        }
    }
    
    with patch("app.clients.legacy_api.legacy_api_client.search_flights", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_response
        
        response = client.post(
            "/api/v1/flights/search",
            json={
                "origin": "HAN",
                "destination": "SGN",
                "departure_date": "2024-12-25",
                "passengers": 1,
                "cabin": "ECONOMY"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["offers"][0]["offer_id"] == "test_offer_1"
        assert data["offers"][0]["total_price"] == 150.0
        assert data["offers"][0]["segments"][0]["flight_number"] == "VN123"
