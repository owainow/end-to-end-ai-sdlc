"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenWeatherMap
    openweathermap_api_key: str = Field(
        ...,
        description="OpenWeatherMap API key",
    )
    openweathermap_base_url: str = Field(
        default="https://api.openweathermap.org/data/2.5",
        description="OpenWeatherMap API base URL",
    )

    # Cache
    cache_ttl_seconds: int = Field(
        default=900,
        ge=60,
        le=3600,
        description="Cache TTL in seconds (15 minutes default)",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )

    # HTTP Client
    http_timeout_seconds: float = Field(
        default=10.0,
        ge=1.0,
        le=30.0,
        description="HTTP request timeout in seconds",
    )

    # Environment
    environment: Literal["dev", "staging", "prod"] = Field(
        default="dev",
        description="Deployment environment",
    )

    # API
    api_version: str = Field(
        default="v1",
        description="API version prefix",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()  # type: ignore[call-arg]
