"""Application layer interfaces (ports)."""

from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities import ForecastData, WeatherData, WeatherRequest


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


class ForecastProviderPort(ABC):
    """Port for weather forecast providers."""

    @abstractmethod
    async def get_forecast(self, request: WeatherRequest) -> ForecastData:
        """Fetch forecast data for a city.

        Args:
            request: The weather request containing city and units.

        Returns:
            ForecastData entity with multi-day forecast.

        Raises:
            CityNotFoundError: If the city cannot be found.
            WeatherProviderError: If the provider fails.
            RateLimitExceededError: If rate limit is exceeded.
        """
        ...


class CachePort(ABC):
    """Port for caching weather data."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieve cached data.

        Args:
            key: The cache key.

        Returns:
            Cached value or None if not found/expired.
        """
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store data in cache.

        Args:
            key: The cache key.
            value: The value to cache.
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
