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
    icon_code: str
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

    city: str = ""
    units: UnitSystem = UnitSystem.METRIC
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Validate request parameters."""
        trimmed_city = self.city.strip() if self.city else ""
        if not self.coordinates and not trimmed_city:
            msg = "Either city or coordinates (lat and lon) must be provided"
            raise ValueError(msg)

        if trimmed_city:
            if len(trimmed_city) > 100:
                msg = "City name must not exceed 100 characters"
                raise ValueError(msg)
            if not any(char.isalpha() for char in trimmed_city):
                msg = "City name must contain letters and cannot consist only of numbers or special characters"
                raise ValueError(msg)

    @property
    def cache_key(self) -> str:
        """Generate cache key for this request."""
        if self.coordinates:
            # Round coordinates to 2 decimal places for cache efficiency
            lat = round(self.coordinates.latitude, 2)
            lon = round(self.coordinates.longitude, 2)
            return f"weather:coords:{lat},{lon}:{self.units.value}"
        normalized_city = self.city.strip().lower()
        return f"weather:{normalized_city}:{self.units.value}"
