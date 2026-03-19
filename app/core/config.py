from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Flight Booking BFF API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Legacy API Configuration
    LEGACY_API_BASE_URL: str = "https://mock-travel-api.vercel.app"
    LEGACY_API_TIMEOUT: int = 30
    LEGACY_API_SIMULATE_ISSUES: bool = False

    # Resilience Configuration
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    RETRY_STATUS_CODES: list[int] = [429, 503]

    # Cache Configuration
    CACHE_DIR: str = ".cache"
    AIRPORT_CACHE_TTL: int = 86400  # 24 hours

    # Other Configuration
    DEBUG: bool = False
    CACHE_TTL: int = 3600
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
