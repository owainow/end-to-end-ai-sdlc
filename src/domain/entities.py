"""Domain entities for the Weather App."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects import Coordinates, UnitSystem, WeatherCondition


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
        # Either city or coordinates must be provided
        if not self.coordinates and (not self.city or not self.city.strip()):
            msg = "Either city name or coordinates must be provided"
            raise ValueError(msg)
        if self.city and len(self.city) > 100:
            msg = "City name cannot exceed 100 characters"
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


@dataclass(frozen=True)
class DailyForecast:
    """Daily forecast value object representing a single day's summary."""

    date: str
    temp_min: float
    temp_max: float
    condition: str
    icon_code: str
    condition_code: WeatherCondition = WeatherCondition.UNKNOWN

    def __post_init__(self) -> None:
        """Derive condition_code if not explicitly set."""
        if self.condition_code == WeatherCondition.UNKNOWN and self.condition:
            object.__setattr__(
                self, "condition_code", WeatherCondition.from_string(self.condition)
            )


@dataclass(frozen=True)
class ForecastData:
    """Forecast data entity representing 5-day weather forecast."""

    city_name: str
    country: str
    coordinates: Coordinates
    units: UnitSystem
    daily_forecasts: list[DailyForecast]
    timestamp: datetime

    def __post_init__(self) -> None:
        """Validate forecast data invariant."""
        if len(self.daily_forecasts) != 5:
            msg = f"ForecastData must contain exactly 5 daily forecasts, got {len(self.daily_forecasts)}"
            raise ValueError(msg)


@dataclass(frozen=True)
class ForecastRequest:
    """Request entity for 5-day forecast queries."""

    city: str
    units: UnitSystem = UnitSystem.METRIC

    def __post_init__(self) -> None:
        """Validate request parameters."""
        from src.domain.exceptions import InvalidCityNameError

        if not self.city or not self.city.strip():
            msg = "City name cannot be empty or whitespace"
            raise InvalidCityNameError(self.city, msg)
        if len(self.city) > 100:
            msg = "City name cannot exceed 100 characters"
            raise InvalidCityNameError(self.city, msg)

    @property
    def cache_key(self) -> str:
        """Generate cache key for this forecast request."""
        normalized_city = self.city.strip().lower()
        return f"forecast:{normalized_city}:{self.units.value}"


@dataclass(frozen=True)
class RawForecastInterval:
    """Raw 3-hour forecast interval data point from provider."""

    dt: datetime
    temp: float
    condition: str
    icon_code: str
    condition_code: WeatherCondition = WeatherCondition.UNKNOWN

    def __post_init__(self) -> None:
        """Derive condition_code if not explicitly set."""
        if self.condition_code == WeatherCondition.UNKNOWN and self.condition:
            object.__setattr__(
                self, "condition_code", WeatherCondition.from_string(self.condition)
            )


@dataclass(frozen=True)
class RawForecastData:
    """Raw 5-day forecast payload from provider."""

    city_name: str
    country: str
    coordinates: Coordinates
    timezone_offset: int
    intervals: list[RawForecastInterval]
