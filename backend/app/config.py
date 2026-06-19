"""Application Configuration"""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Always resolve .env relative to this file (backend/app/config.py → backend/.env)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings from environment variables"""

    database_url: str
    google_sheets_api_key: str = ""
    google_sheets_credentials_file: str = "./credentials.json"
    webull_app_key: str = ""
    webull_app_secret: str = ""
    python_env: str = "development"
    log_level: str = "INFO"
    port: int = 8000
    redis_url: str = "redis://localhost:6379/0"
    scheduler_enabled: bool = True

    class Config:
        env_file = str(_ENV_FILE)


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()


settings = get_settings()
