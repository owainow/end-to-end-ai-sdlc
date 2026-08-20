"""Pydantic schemas for API request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects import UnitSystem, WeatherCondition


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


class DailyForecastResponse(BaseModel):
    """Daily forecast response schema."""

    date: str = Field(..., description="Forecast date in YYYY-MM-DD format")
    temp_min: float = Field(..., description="Minimum temperature for the day")
    temp_max: float = Field(..., description="Maximum temperature for the day")
    condition: str = Field(..., description="Representative weather condition summary")
    condition_code: WeatherCondition = Field(
        default=WeatherCondition.UNKNOWN,
        description="Machine-readable weather condition enum",
    )
    icon_code: str = Field(..., description="Weather icon code")


class ForecastResponse(BaseModel):
    """5-day weather forecast API response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "London",
                "country": "GB",
                "coordinates": {"latitude": 51.5074, "longitude": -0.1278},
                "units": "metric",
                "daily_forecasts": [
                    {
                        "date": "2026-08-19",
                        "temp_min": 14.0,
                        "temp_max": 22.5,
                        "condition": "clear sky",
                        "condition_code": "clear",
                        "icon_code": "01d",
                    },
                    {
                        "date": "2026-08-20",
                        "temp_min": 15.0,
                        "temp_max": 23.0,
                        "condition": "few clouds",
                        "condition_code": "clouds",
                        "icon_code": "02d",
                    },
                    {
                        "date": "2026-08-21",
                        "temp_min": 13.5,
                        "temp_max": 20.0,
                        "condition": "light rain",
                        "condition_code": "rain",
                        "icon_code": "10d",
                    },
                    {
                        "date": "2026-08-22",
                        "temp_min": 12.0,
                        "temp_max": 19.5,
                        "condition": "scattered clouds",
                        "condition_code": "clouds",
                        "icon_code": "03d",
                    },
                    {
                        "date": "2026-08-23",
                        "temp_min": 14.5,
                        "temp_max": 21.0,
                        "condition": "clear sky",
                        "condition_code": "clear",
                        "icon_code": "01d",
                    },
                ],
                "timestamp": "2026-08-19T12:00:00Z",
            }
        }
    )

    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code (ISO 3166)")
    coordinates: dict[str, float] = Field(
        ..., description="Geographic coordinates (latitude, longitude)"
    )
    units: UnitSystem = Field(..., description="Temperature units (metric/imperial)")
    daily_forecasts: list[DailyForecastResponse] = Field(
        ..., description="Array of 5 consecutive daily forecasts"
    )
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
