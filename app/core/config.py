"""
Centralized configuration from environment variables.
All secrets, URLs, and credentials loaded here — never hardcoded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # ─── Server ───
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # ─── Security / JWT ───
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # ─── Microservice URLs ───
    INVENTORY_SERVICE_URL: str = "http://localhost:8002"
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    PAYMENT_SERVICE_URL: str = "http://localhost:8004"

    # ─── User Portal ───
    USER_PORTAL_URL: str = ""
    USER_PORTAL_API_KEY: str = ""
    USER_PORTAL_API_SECRET: str = ""

    # ─── Service API Credentials ───
    INVENTORY_SERVICE_API_KEY: str = ""
    INVENTORY_SERVICE_API_SECRET: str = ""
    PAYMENT_SERVICE_API_KEY: str = ""
    PAYMENT_SERVICE_API_SECRET: str = ""
    ORDER_SERVICE_API_KEY: str = ""
    ORDER_SERVICE_API_SECRET: str = ""

    # ─── CORS ───
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ─── Rate Limiting ───
    RATE_LIMIT: str = "100/minute"

    # ─── Project Meta ───
    PROJECT_NAME: str = "Store BFF"
    API_V1_STR: str = "/api"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
