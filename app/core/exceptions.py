from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class UnifiedError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }

class LegacyAPIError(UnifiedError):
    """Exception raised when the legacy API returns an error."""
    pass

class RateLimitError(LegacyAPIError):
    def __init__(self, message: str = "Too Many Requests", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )

class ServiceUnavailableError(LegacyAPIError):
    def __init__(self, message: str = "Service Unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )

class NotFoundError(UnifiedError):
    def __init__(self, message: str = "Resource Not Found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )
