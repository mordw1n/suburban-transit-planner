import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Suburban Transit Planner"
    VERSION: str = "0.1.0-mvp"
    API_V1_PREFIX: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost:5432/transit_planner"
    )
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TTL_SEC: int = 86400
    CACHE_DELAYS_TTL_SEC: int = 180
    
    YANDEX_API_KEY: str = os.getenv("YANDEX_API_KEY", "")
    YANDEX_API_BASE_URL: str = "https://api.rasp.yandex.net/v3.0"
    
    CIRCUIT_BREAKER_FAIL_MAX: int = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 60
    
    class Config:
        case_sensitive = True

settings = Settings()
