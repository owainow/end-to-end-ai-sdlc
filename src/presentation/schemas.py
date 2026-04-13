"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects import UnitSystem


class WeatherResponse(BaseModel):
    """Weather API response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "London",
                "country": "GB",
                "coordinates": {"latitude": 51.5074, "longitude": -0.1278},
                "temperature": 15.2,
                "feels_like": 14.8,
                "humidity": 72,
                "wind_speed": 4.5,
                "pressure": 1013,
                "visibility": 10000,
                "description": "scattered clouds",
                "icon_code": "03d",
                "units": "metric",
                "timestamp": "2024-01-19T15:30:00Z",
            }
        }
    )

    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code (ISO 3166)")
    coordinates: dict[str, float] = Field(
        ..., description="Geographic coordinates (latitude, longitude)"
    )
    temperature: float = Field(..., description="Current temperature")
    feels_like: float = Field(..., description="Feels like temperature")
    humidity: int = Field(..., ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(..., ge=0, description="Wind speed")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    visibility: int = Field(..., ge=0, description="Visibility in meters")
    description: str = Field(..., description="Weather condition description")
    icon_code: str = Field(..., description="Weather icon code")
    units: UnitSystem = Field(..., description="Temperature units (metric/imperial)")
    timestamp: datetime = Field(..., description="Data timestamp (UTC)")


class ErrorResponse(BaseModel):
    """Error response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "CITY_NOT_FOUND",
                    "message": "City not found: InvalidCity",
                    "retry_after": None,
                }
            }
        }
    )

    error: dict[str, str | int | None] = Field(
        ...,
        description="Error details including code, message, and optional retry_after",
    )


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")


class ForecastDayResponse(BaseModel):
    """Forecast day API response schema."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    day_label: str = Field(..., description="Day label (Today, Mon, Tue, etc.)")
    temp_high: float = Field(..., description="High temperature for the day")
    temp_low: float = Field(..., description="Low temperature for the day")
    humidity: int = Field(..., ge=0, le=100, description="Average humidity percentage")
    wind_speed: float = Field(..., ge=0, description="Peak wind speed")
    description: str = Field(..., description="Weather condition description")
    icon_code: str = Field(..., description="Weather icon code")


class ForecastResponse(BaseModel):
    """Forecast API response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "London",
                "country": "GB",
                "coordinates": {"latitude": 51.5074, "longitude": -0.1278},
                "units": "metric",
                "days": [
                    {
                        "date": "2024-01-19",
                        "day_label": "Today",
                        "temp_high": 15.2,
                        "temp_low": 10.1,
                        "humidity": 72,
                        "wind_speed": 4.5,
                        "description": "scattered clouds",
                        "icon_code": "03d",
                    }
                ],
                "timestamp": "2024-01-19T15:30:00Z",
            }
        }
    )

    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code (ISO 3166)")
    coordinates: dict[str, Any] = Field(
        ..., description="Geographic coordinates (latitude, longitude)"
    )
    units: UnitSystem = Field(..., description="Temperature units (metric/imperial)")
    days: list[ForecastDayResponse] = Field(..., description="Daily forecast entries")
    timestamp: datetime = Field(..., description="Data timestamp (UTC)")
