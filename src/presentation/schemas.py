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


class ErrorDetail(BaseModel):
    """Detailed error payload schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "UNPROCESSABLE_ENTITY",
                "message": "City name cannot be empty",
                "target": "city",
                "details": [],
                "correlationId": "req-12345678-1234-4321-abcd-1234567890ab",
                "retry_after": None,
            }
        }
    )

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    target: str | None = Field(
        default=None, description="Target parameter or field that caused the error"
    )
    details: list[dict[str, Any]] = Field(
        default_factory=list, description="Sub-error details"
    )
    correlationId: str = Field(
        ..., description="Unique request correlation ID for tracing"
    )
    retry_after: int | None = Field(
        default=None, description="Seconds to wait before retrying (if applicable)"
    )


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")
