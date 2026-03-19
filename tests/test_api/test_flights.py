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
                                                    "airport": {"code": "HAN", "terminal": "T1"},
                                                    "scheduled_time": "20241225055000"
                                                },
                                                "arrival_info": {
                                                    "airport": {"code": "SGN", "terminal": "T2"},
                                                    "scheduled_time": "20241225080000"
                                                },
                                                "carrier": {"operating": "VN", "number": "VN123"},
                                                "duration_minutes": 130,
                                                "equipment": {"aircraft_code": "359"}
                                            }
                                        ]
                                    }
                                ]
                            },
                            "pricing": {
                                "total": 150.0,
                                "base_fare": 130.0,
                                "currency": "USD",
                                "taxes_fees": {
                                    "total_tax": 20.0,
                                    "tax_breakdown": [{"code": "YQ", "amount": 20.0}]
                                }
                            },
                            "refundable": False,
                            "cabin_class": "Y",
                            "seats_remaining": 5,
                            "fare_basis": "YFL",
                            "validating_carrier": "VN",
                            "baggage": {
                                "checked": {"pieces": 1, "weight_kg": 20},
                                "cabin_baggage": {"pieces": 1, "weight_kg": 7}
                            }
                        }
                    ]
                }
            }
        }
    }
    
    with patch("app.clients.legacy_api.legacy_api_client.search_flights", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_response
        
        # Mock airport service as well to avoid actual cache/file access
        with patch("app.services.airports.airport_service.get_airport", new_callable=AsyncMock) as mock_airport:
            mock_airport.return_value = AsyncMock(city="Mock City")

            response = client.post(
                "/api/v1/flights/search",
                json={
                    "origin": "HAN",
                    "destination": "SGN",
                    "departureDate": "2024-12-25",
                    "passengers": 1,
                    "cabin": "ECONOMY"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check camelCase keys and new fields
            assert data["outboundCount"] == 1
            offer = data["outboundOffers"][0]
            assert offer["offerId"] == "test_offer_1"
            assert offer["pricing"]["total"] == 150.0
            assert offer["pricing"]["base"] == 130.0
            assert offer["pricing"]["tax"] == 20.0
            assert offer["pricing"]["taxBreakdown"][0]["code"] == "YQ"
            assert offer["segments"][0]["flightNumber"] == "VN123"
            assert offer["segments"][0]["originTerminal"] == "T1"
            assert offer["segments"][0]["aircraftCode"] == "359"
            assert offer["baggage"]["checkedPieces"] == 1
            assert offer["isRefundable"] is False
            assert offer["seatsRemaining"] == 5
