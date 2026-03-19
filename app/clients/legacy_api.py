import httpx
import logging
import asyncio
import time
from typing import Any, Dict, List, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.core.config import settings
from app.clients.schemas import legacy as legacy_schemas
from app.core.exceptions import LegacyAPIError, RateLimitError, ServiceUnavailableError, NotFoundError

# Configure logger for visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_retry(retry_state):
    """Callback function for tenacity to log retry attempts."""
    logger.warning(
        f"--- Resilience: Retrying Legacy API call... Attempt #{retry_state.attempt_number}. "
        f"Reason: {retry_state.outcome.exception()}"
    )

class CircuitBreaker:
    """A simple Circuit Breaker implementation to protect the system from cascading failures."""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def is_available(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker: State changed to HALF_OPEN - Testing legacy system...")
                return True
            return False
        return True

    def record_success(self):
        if self.state != "CLOSED":
            logger.info("Circuit Breaker: State changed to CLOSED - Legacy system recovered.")
        self.failures = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            if self.state != "OPEN":
                logger.error(f"Circuit Breaker: State changed to OPEN after {self.failures} consecutive failures. Blocking requests for {self.recovery_timeout}s.")
            self.state = "OPEN"

class LegacyAPIClient:
    def __init__(
        self, 
        base_url: str = settings.LEGACY_API_BASE_URL, 
        timeout: int = settings.LEGACY_API_TIMEOUT,
        simulate_issues: bool = settings.LEGACY_API_SIMULATE_ISSUES
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.simulate_issues = simulate_issues
        self.cb = CircuitBreaker()

    @retry(
        retry=retry_if_exception_type((ServiceUnavailableError, RateLimitError)),
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        before_sleep=log_retry,
        reraise=True
    )
    async def _request(self, method: str, path: str, simulate_issues: Optional[bool] = None, **kwargs) -> Any:
        # 1. Check Circuit Breaker
        if not self.cb.is_available():
            raise ServiceUnavailableError(message="Hệ thống Legacy đang gặp sự cố và bị ngắt mạch (Circuit Breaker OPEN). Vui lòng thử lại sau.")

        url = f"{self.base_url}/{path.lstrip('/')}"
        should_simulate = simulate_issues if simulate_issues is not None else self.simulate_issues
        
        params = kwargs.get("params") or {}
        if should_simulate:
            params["simulate_issues"] = "true"
        kwargs["params"] = params
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, **kwargs)
                
                if response.is_success:
                    self.cb.record_success()
                    return response.json()
                
                # Handle error statuses
                status_code = response.status_code
                error_body = self._parse_error_body(response)
                
                # Record failure for Circuit Breaker for system-level errors
                if status_code in [429, 503, 500]:
                    self.cb.record_failure()

                if status_code == 429:
                    raise RateLimitError(message=f"Lỗi giới hạn lượt gọi (429): {error_body.get('message')}", details=error_body)
                elif status_code == 503:
                    raise ServiceUnavailableError(message=f"Lỗi dịch vụ tạm thời (503): {error_body.get('message')}", details=error_body)
                elif status_code == 404:
                    raise NotFoundError(message=f"Không tìm thấy dữ liệu (404): {error_body.get('message')}", details=error_body)
                else:
                    raise LegacyAPIError(
                        code=f"LEGACY_ERROR_{status_code}",
                        message=error_body.get("message", f"Legacy API error {status_code}"),
                        status_code=status_code,
                        details=error_body
                    )
                    
            except (httpx.RequestError, httpx.TimeoutException) as e:
                self.cb.record_failure()
                logger.error(f"--- Resilience: Network error connecting to Legacy API: {str(e)}")
                raise ServiceUnavailableError(message="Không thể kết nối tới hệ thống Legacy.")

    def _parse_error_body(self, response: httpx.Response) -> Dict[str, Any]:
        """Attempt to parse the legacy API's various error formats."""
        try:
            body = response.json()
            message = body.get("message") or body.get("error")
            if isinstance(body.get("data"), dict):
                message = message or body["data"].get("error")
            
            code = body.get("code") or body.get("status")
            
            return {
                "message": str(message) if message else "Unknown legacy error",
                "code": str(code) if code else "UNKNOWN",
                "raw": body
            }
        except:
            return {
                "message": response.text[:200] or "Empty error response",
                "code": "RAW_RESPONSE",
                "raw": response.text
            }

    async def search_flights(self, request_data: legacy_schemas.SearchRequest, simulate_issues: Optional[bool] = None) -> Dict[str, Any]:
        return await self._request("POST", "/api/v1/flightsearch", simulate_issues=simulate_issues, json=request_data.model_dump())

    async def get_offer_details(self, offer_id: str, simulate_issues: Optional[bool] = None) -> Dict[str, Any]:
        return await self._request("GET", f"/api/v2/offer/{offer_id}", simulate_issues=simulate_issues)

    async def create_booking(self, request_data: legacy_schemas.CreateBookingRequest, simulate_issues: Optional[bool] = None) -> Dict[str, Any]:
        return await self._request("POST", "/booking/create", simulate_issues=simulate_issues, json=request_data.model_dump())

    async def get_reservation(self, ref: str, simulate_issues: Optional[bool] = None) -> Dict[str, Any]:
        return await self._request("GET", f"/api/v1/reservations/{ref}", simulate_issues=simulate_issues)

    async def list_airports(self, simulate_issues: Optional[bool] = None) -> List[str]:
        data = await self._request("GET", "/api/airports", simulate_issues=simulate_issues)
        airports_list = data.get("airports") or data.get("response", {}).get("airports", [])
        return [airport["code"] for airport in airports_list if "code" in airport]

    async def get_airport(self, code: str, simulate_issues: Optional[bool] = None) -> Dict[str, Any]:
        return await self._request("GET", f"/api/airports/{code}", simulate_issues=simulate_issues)

legacy_api_client = LegacyAPIClient()
