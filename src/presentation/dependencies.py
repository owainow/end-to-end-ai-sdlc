"""Dependency injection for FastAPI."""

from functools import lru_cache

from fastapi import HTTPException

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


def validate_city_name(city: str) -> str:
    """Validate and trim city name according to boundary rules.

    Args:
        city: Raw city query parameter string.

    Returns:
        Trimmed valid city string.

    Raises:
        HTTPException: Status 422 if empty, over 100 chars, or contains no letters.
    """
    trimmed = city.strip()
    if not trimmed:
        raise HTTPException(
            status_code=422,
            detail={"message": "City name cannot be empty", "target": "city"},
        )
    if len(trimmed) > 100:
        raise HTTPException(
            status_code=422,
            detail={"message": "City name must not exceed 100 characters", "target": "city"},
        )
    if not any(char.isalpha() for char in trimmed):
        raise HTTPException(
            status_code=422,
            detail={
                "message": "City name must contain letters and cannot consist only of numbers or special characters",
                "target": "city",
            },
        )
    return trimmed


def validate_weather_query_params(
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> tuple[str | None, float | None, float | None]:
    """Validate query parameters for weather endpoint at the API boundary.

    Enforces:
    1. Incomplete coordinate check (lat without lon or vice versa).
    2. City boundary validation if city is provided.
    3. Requirement of either a valid city or complete coordinates.

    Args:
        city: Optional city query parameter.
        lat: Optional latitude query parameter.
        lon: Optional longitude query parameter.

    Returns:
        Tuple of (validated_city, lat, lon).
    """
    if (lat is None) != (lon is None):
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Both lat and lon must be provided together, or neither",
                "target": "coordinates",
            },
        )

    validated_city: str | None = None
    if city is not None:
        validated_city = validate_city_name(city)

    has_coords = lat is not None and lon is not None
    if not validated_city and not has_coords:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Either city or coordinates (lat and lon) must be provided",
                "target": "city",
            },
        )

    return validated_city, lat, lon

