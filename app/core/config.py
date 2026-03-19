from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Flight Booking BFF API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Legacy API Configuration
    LEGACY_API_BASE_URL: str = "https://mock-travel-api.vercel.app"
    LEGACY_API_TIMEOUT: int = 30

    # Cache Configuration
    CACHE_DIR: str = ".cache"
    AIRPORT_CACHE_TTL: int = 86400  # 24 hours

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
