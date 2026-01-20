"""Domain entities for the Weather App."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects import Coordinates, UnitSystem


@dataclass(frozen=True)
class WeatherData:
    """Weather data entity representing current weather conditions."""

    city_name: str
    country: str
    coordinates: Coordinates
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    pressure: int
    visibility: int
    description: str
    units: UnitSystem
    timestamp: datetime

    @property
    def temperature_display(self) -> str:
        """Return formatted temperature with unit symbol."""
        symbol = "°C" if self.units == UnitSystem.METRIC else "°F"
        return f"{self.temperature:.1f}{symbol}"

    @property
    def wind_speed_display(self) -> str:
        """Return formatted wind speed with unit."""
        unit = "m/s" if self.units == UnitSystem.METRIC else "mph"
        return f"{self.wind_speed:.1f} {unit}"

    @property
    def location_display(self) -> str:
        """Return formatted location string."""
        return f"{self.city_name}, {self.country}"


@dataclass(frozen=True)
class WeatherRequest:
    """Request entity for weather queries."""

    city: str
    units: UnitSystem = UnitSystem.METRIC

    def __post_init__(self) -> None:
        """Validate request parameters."""
        if not self.city or not self.city.strip():
            msg = "City name cannot be empty"
            raise ValueError(msg)
        if len(self.city) > 100:
            msg = "City name cannot exceed 100 characters"
            raise ValueError(msg)

    @property
    def cache_key(self) -> str:
        """Generate cache key for this request."""
        normalized_city = self.city.strip().lower()
        return f"weather:{normalized_city}:{self.units.value}"
