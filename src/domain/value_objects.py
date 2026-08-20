"""Value objects for the Weather App domain."""

from dataclasses import dataclass
from enum import StrEnum


class UnitSystem(StrEnum):
    """Temperature unit systems."""

    METRIC = "metric"  # Celsius
    IMPERIAL = "imperial"  # Fahrenheit


class WeatherCondition(StrEnum):
    """Machine-readable weather condition enum."""

    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    DRIZZLE = "drizzle"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    MIST = "mist"
    SMOKE = "smoke"
    HAZE = "haze"
    DUST = "dust"
    FOG = "fog"
    SAND = "sand"
    ASH = "ash"
    SQUALL = "squall"
    TORNADO = "tornado"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, value: str | None) -> "WeatherCondition":
        """Convert a string condition into a WeatherCondition enum member safely."""
        if not value:
            return cls.UNKNOWN
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError:
            pass

        # Alias / keyword mapping for common weather descriptions
        aliases: dict[str, WeatherCondition] = {
            "sun": cls.CLEAR,
            "sunny": cls.CLEAR,
            "cloud": cls.CLOUDS,
            "cloudy": cls.CLOUDS,
            "overcast": cls.CLOUDS,
            "storm": cls.THUNDERSTORM,
            "thunder": cls.THUNDERSTORM,
            "shower": cls.RAIN,
            "sleet": cls.SNOW,
        }
        for alias, member in aliases.items():
            if alias in normalized:
                return member

        for member in cls:
            if member == cls.UNKNOWN:
                continue
            if member.value in normalized or normalized in member.value:
                return member
        return cls.UNKNOWN


@dataclass(frozen=True)
class Coordinates:
    """Geographic coordinates value object."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate coordinates are within valid ranges."""
        if not -90 <= self.latitude <= 90:
            msg = f"Latitude must be between -90 and 90, got {self.latitude}"
            raise ValueError(msg)
        if not -180 <= self.longitude <= 180:
            msg = f"Longitude must be between -180 and 180, got {self.longitude}"
            raise ValueError(msg)

    def __str__(self) -> str:
        """Return human-readable coordinate string."""
        return f"({self.latitude:.4f}, {self.longitude:.4f})"
