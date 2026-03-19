import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from app.clients.legacy_api import LegacyAPIClient
from app.core.exceptions import RateLimitError, ServiceUnavailableError, UnifiedError
from app.core.config import settings

@pytest.mark.asyncio
async def test_retry_on_503():
    """Test that the client retries on 503 Service Unavailable."""
    client = LegacyAPIClient(simulate_issues=False)
    
    mock_response_503 = MagicMock(spec=httpx.Response)
    mock_response_503.status_code = 503
    mock_response_503.is_success = False
    mock_response_503.json.return_value = {"error": "Service Temporarily Unavailable"}
    
    mock_response_200 = MagicMock(spec=httpx.Response)
    mock_response_200.status_code = 200
    mock_response_200.is_success = True
    mock_response_200.json.return_value = {"status": "success"}
    
    # We want it to fail once with 503 and then succeed
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = [mock_response_503, mock_response_200]
        
        result = await client._request("GET", "/test")
        
        assert result == {"status": "success"}
        assert mock_request.call_count == 2

@pytest.mark.asyncio
async def test_retry_on_429():
    """Test that the client retries on 429 Too Many Requests."""
    client = LegacyAPIClient(simulate_issues=False)
    
    mock_response_429 = MagicMock(spec=httpx.Response)
    mock_response_429.status_code = 429
    mock_response_429.is_success = False
    mock_response_429.json.return_value = {"message": "Rate limit exceeded", "code": "RATE_LIMIT"}
    
    mock_response_200 = MagicMock(spec=httpx.Response)
    mock_response_200.status_code = 200
    mock_response_200.is_success = True
    mock_response_200.json.return_value = {"status": "success"}
    
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = [mock_response_429, mock_response_200]
        
        result = await client._request("GET", "/test")
        
        assert result == {"status": "success"}
        assert mock_request.call_count == 2

@pytest.mark.asyncio
async def test_max_retries_exceeded():
    """Test that the client eventually raises an error after max retries."""
    client = LegacyAPIClient(simulate_issues=False)
    
    mock_response_503 = MagicMock(spec=httpx.Response)
    mock_response_503.status_code = 503
    mock_response_503.is_success = False
    mock_response_503.json.return_value = {"error": "Still Down"}
    
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response_503
        
        with pytest.raises(ServiceUnavailableError):
            await client._request("GET", "/test")
        
        # settings.MAX_RETRIES is 3, so it should be called 3 times total
        assert mock_request.call_count == settings.MAX_RETRIES

@pytest.mark.asyncio
async def test_simulate_issues_flag():
    """Test that simulate_issues=true is added to params when enabled."""
    client = LegacyAPIClient(simulate_issues=True)
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"status": "ok"}
    
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        await client._request("GET", "/test", params={"foo": "bar"})
        
        args, kwargs = mock_request.call_args
        assert kwargs["params"]["simulate_issues"] == "true"
        assert kwargs["params"]["foo"] == "bar"

@pytest.mark.asyncio
async def test_error_unification():
    """Test that various legacy error formats are unified."""
    client = LegacyAPIClient(simulate_issues=False)
    
    # Format 1: {"error": "message"}
    mock_resp_1 = MagicMock(spec=httpx.Response)
    mock_resp_1.status_code = 400
    mock_resp_1.is_success = False
    mock_resp_1.json.return_value = {"error": "Invalid request parameters"}
    
    # Format 2: {"message": "message", "code": "code"}
    mock_resp_2 = MagicMock(spec=httpx.Response)
    mock_resp_2.status_code = 400
    mock_resp_2.is_success = False
    mock_resp_2.json.return_value = {"message": "Something went wrong", "code": "ERR_123"}
    
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        # Test Format 1
        mock_request.return_value = mock_resp_1
        try:
            await client._request("GET", "/test")
        except UnifiedError as e:
            err_dict = e.to_dict()
            assert err_dict["error"]["message"] == "Invalid request parameters"
            
        # Test Format 2
        mock_request.return_value = mock_resp_2
        try:
            await client._request("GET", "/test")
        except UnifiedError as e:
            err_dict = e.to_dict()
            assert err_dict["error"]["message"] == "Something went wrong"
            assert err_dict["error"]["details"]["code"] == "ERR_123"
