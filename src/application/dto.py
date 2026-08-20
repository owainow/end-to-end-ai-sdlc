"""Application layer Data Transfer Objects (DTOs)."""

from dataclasses import dataclass

from src.domain.entities import WeatherData


@dataclass(frozen=True)
class WeatherResult:
    """Application DTO representing the result of a weather query."""

    weather_data: WeatherData
    easter_egg: str | None = None
