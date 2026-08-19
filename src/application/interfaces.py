"""Application layer interfaces (ports)."""

from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities import (
    ForecastData,
    RawForecastData,
    WeatherData,
    WeatherRequest,
)
from src.domain.value_objects import UnitSystem


class WeatherProviderPort(ABC):
    """Port for weather data providers."""

    @abstractmethod
    async def get_weather(self, request: WeatherRequest) -> WeatherData:
        """Fetch weather data for a city.

        Args:
            request: The weather request containing city and units.

        Returns:
            WeatherData entity with current conditions.

        Raises:
            CityNotFoundError: If the city cannot be found.
            WeatherProviderError: If the provider fails.
            RateLimitExceededError: If rate limit is exceeded.
        """
        ...

    @abstractmethod
    async def get_forecast_raw(self, city: str, units: UnitSystem) -> RawForecastData:
        """Fetch raw 5-day forecast data for a city.

        Args:
            city: The city name.
            units: The temperature unit system.

        Returns:
            RawForecastData containing 3-hour intervals and timezone offset.

        Raises:
            CityNotFoundError: If the city cannot be found.
            WeatherProviderError: If the provider fails.
            RateLimitExceededError: If rate limit is exceeded.
        """
        ...


class CachePort(ABC):
    """Port for caching weather and forecast data."""

    @abstractmethod
    def get(self, key: str) -> WeatherData | ForecastData | None:
        """Retrieve cached weather or forecast data.

        Args:
            key: The cache key.

        Returns:
            Cached WeatherData, ForecastData, or None if not found/expired.
        """
        ...

    @abstractmethod
    def set(self, key: str, value: WeatherData | ForecastData, ttl_seconds: int) -> None:
        """Store weather or forecast data in cache.

        Args:
            key: The cache key.
            value: The WeatherData or ForecastData to cache.
            ttl_seconds: Time-to-live in seconds.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove an entry from cache.

        Args:
            key: The cache key to delete.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached entries."""
        ...


class LoggerPort(ABC):
    """Port for structured logging."""

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        ...

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        ...

    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        ...
