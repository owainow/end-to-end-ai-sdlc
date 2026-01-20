"""Dependency injection for FastAPI."""

from functools import lru_cache

from src.application.use_cases import GetWeatherUseCase
from src.infrastructure.cache import InMemoryCache
from src.infrastructure.config import get_settings
from src.infrastructure.logging import StructlogAdapter
from src.infrastructure.weather_provider import OpenWeatherMapClient

# Singleton instances
_cache: InMemoryCache | None = None
_logger: StructlogAdapter | None = None


def get_cache() -> InMemoryCache:
    """Get or create the cache singleton."""
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
    return _cache


def get_logger() -> StructlogAdapter:
    """Get or create the logger singleton."""
    global _logger
    if _logger is None:
        _logger = StructlogAdapter()
    return _logger


@lru_cache
def get_weather_provider() -> OpenWeatherMapClient:
    """Get cached weather provider instance."""
    settings = get_settings()
    return OpenWeatherMapClient(
        api_key=settings.openweathermap_api_key,
        base_url=settings.openweathermap_base_url,
        timeout_seconds=settings.http_timeout_seconds,
    )


def get_weather_use_case() -> GetWeatherUseCase:
    """Get the GetWeatherUseCase with all dependencies."""
    settings = get_settings()
    return GetWeatherUseCase(
        weather_provider=get_weather_provider(),
        cache=get_cache(),
        logger=get_logger(),
        cache_ttl_seconds=settings.cache_ttl_seconds,
    )
