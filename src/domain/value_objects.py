"""Value objects for the Weather App domain."""

from dataclasses import dataclass
from enum import Enum


class UnitSystem(str, Enum):
    """Temperature unit systems."""

    METRIC = "metric"  # Celsius
    IMPERIAL = "imperial"  # Fahrenheit


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
