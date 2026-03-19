from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_offer_details_v2_accuracy():
    # Mocking the legacy API offer detail response (GDS v2 style)
    mock_legacy_detail = {
        "data": {
            "offer": {
                "id": "93f1d242d6fddd80",
                "status": "LIVE",
                "fare_details": {
                    "rules": {
                        "refund": {
                            "allowed": False,
                            "penalty": {"amount": 150, "currency": "MYR"}
                        },
                        "change": {
                            "allowed": True,
                            "penalty": {"amount": 200, "currency": "MYR"}
                        },
                        "no_show": {
                            "penalty": {"amount": 200, "currency": "MYR"}
                        }
                    },
                    "fare_family": "FLEX"
                },
                "baggage_allowance": {
                    "checked": {"quantity": 1, "max_weight_kg": 30},
                    "carry_on": {"quantity": 1, "max_weight_kg": 7}
                },
                "conditions": {
                    "advance_purchase_days": 7,
                    "min_stay_days": 3,
                    "max_stay_days": 90
                },
                "payment_requirements": {
                    "accepted_methods": ["CC", "DC", "BT"],
                    "time_limit": "20/03/2026 08:46",
                    "instant_ticketing_required": True
                },
                "created_at": "19/03/2026 07:46",
                "expires_at": "20260319082124"
            }
        }
    }

    with patch("app.clients.legacy_api.legacy_api_client.get_offer_details", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_legacy_detail

        response = client.get("/api/v1/flights/offers/93f1d242d6fddd80")
        
        assert response.status_code == 200
        data = response.json()
        
        # 1. Verify NO invented fields
        assert "segments" not in data
        assert "pricing" not in data
        
        # 2. Verify logical accuracy
        assert data["isRefundable"] is False
        
        # 3. Verify new detail fields
        assert data["fareFamily"] == "FLEX"
        assert data["rules"]["refund"]["allowed"] is False
        assert data["rules"]["noShow"]["penalty"]["amount"] == 200
        assert data["baggageAllowance"]["checked"]["quantity"] == 1
        assert data["paymentRequirements"]["acceptedMethods"] == ["CC", "DC", "BT"]
        
        # 4. Verify ISO dates
        assert data["expiresAt"].endswith("Z") or "T" in data["expiresAt"]
        assert data["paymentRequirements"]["timeLimit"].startswith("2026-03-20")
