"""Shared test fixtures for Weather App tests."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities import (
    DailyForecast,
    ForecastData,
    ForecastRequest,
    WeatherData,
)
from src.domain.value_objects import Coordinates, UnitSystem


@pytest.fixture
def sample_coordinates() -> Coordinates:
    """Sample coordinates for London."""
    return Coordinates(latitude=51.5074, longitude=-0.1278)


@pytest.fixture
def sample_weather_data(sample_coordinates: Coordinates) -> WeatherData:
    """Sample weather data for testing."""
    return WeatherData(
        city_name="London",
        country="GB",
        coordinates=sample_coordinates,
        temperature=15.2,
        feels_like=14.8,
        humidity=72,
        wind_speed=4.5,
        pressure=1013,
        visibility=10000,
        description="scattered clouds",
        icon_code="04d",
        units=UnitSystem.METRIC,
        timestamp=datetime.now(UTC),
    )


@pytest.fixture
def sample_daily_forecasts() -> list[DailyForecast]:
    """Sample 5 daily forecasts for testing."""
    return [
        DailyForecast(
            date="2026-08-19",
            temp_min=14.0,
            temp_max=22.5,
            condition="clear sky",
            icon_code="01d",
        ),
        DailyForecast(
            date="2026-08-20",
            temp_min=15.0,
            temp_max=23.0,
            condition="few clouds",
            icon_code="02d",
        ),
        DailyForecast(
            date="2026-08-21",
            temp_min=13.5,
            temp_max=20.0,
            condition="light rain",
            icon_code="10d",
        ),
        DailyForecast(
            date="2026-08-22",
            temp_min=12.0,
            temp_max=19.5,
            condition="scattered clouds",
            icon_code="03d",
        ),
        DailyForecast(
            date="2026-08-23",
            temp_min=14.5,
            temp_max=21.0,
            condition="clear sky",
            icon_code="01d",
        ),
    ]


@pytest.fixture
def sample_forecast_data(
    sample_coordinates: Coordinates, sample_daily_forecasts: list[DailyForecast]
) -> ForecastData:
    """Sample ForecastData entity for testing."""
    return ForecastData(
        city_name="London",
        country="GB",
        coordinates=sample_coordinates,
        units=UnitSystem.METRIC,
        daily_forecasts=sample_daily_forecasts,
        timestamp=datetime.now(UTC),
    )


@pytest.fixture
def sample_forecast_request() -> ForecastRequest:
    """Sample ForecastRequest for testing."""
    return ForecastRequest(city="London", units=UnitSystem.METRIC)


@pytest.fixture
def mock_weather_provider() -> MagicMock:
    """Mock weather provider for testing."""
    from src.application.interfaces import WeatherProviderPort

    provider = MagicMock(spec=WeatherProviderPort)
    provider.get_weather = AsyncMock()
    provider.get_forecast_raw = AsyncMock()
    return provider


@pytest.fixture
def mock_cache() -> MagicMock:
    """Mock cache for testing."""
    from src.application.interfaces import CachePort

    cache = MagicMock(spec=CachePort)
    cache.get = MagicMock(return_value=None)
    cache.set = MagicMock()
    return cache


@pytest.fixture
def openweathermap_response() -> dict[str, Any]:
    """Sample OpenWeatherMap API response."""
    return {
        "coord": {"lon": -0.1278, "lat": 51.5074},
        "weather": [
            {
                "id": 803,
                "main": "Clouds",
                "description": "scattered clouds",
                "icon": "04d",
            }
        ],
        "base": "stations",
        "main": {
            "temp": 15.2,
            "feels_like": 14.8,
            "temp_min": 13.5,
            "temp_max": 17.0,
            "pressure": 1013,
            "humidity": 72,
        },
        "visibility": 10000,
        "wind": {"speed": 4.5, "deg": 250},
        "clouds": {"all": 40},
        "dt": 1705678800,
        "sys": {
            "type": 2,
            "id": 2075535,
            "country": "GB",
            "sunrise": 1705651200,
            "sunset": 1705683600,
        },
        "timezone": 0,
        "id": 2643743,
        "name": "London",
        "cod": 200,
    }


@pytest.fixture
def make_forecast_payload() -> Any:
    """Factory fixture to generate 40 3-hour forecast intervals."""

    def _generate(
        city_name: str = "London",
        country: str = "GB",
        lat: float = 51.5074,
        lon: float = -0.1278,
        timezone_offset: int = 0,
        start_timestamp: int = 1771416000,  # 2026-08-19 12:00:00 UTC
        count: int = 40,
        base_temp: float = 20.0,
    ) -> dict[str, Any]:
        intervals = []
        for i in range(count):
            dt = start_timestamp + i * 3 * 3600
            temp = base_temp + (i % 8) * 1.5 - (i % 4) * 0.5
            intervals.append(
                {
                    "dt": dt,
                    "main": {
                        "temp": round(temp, 1),
                        "temp_min": round(temp - 2.0, 1),
                        "temp_max": round(temp + 2.0, 1),
                        "pressure": 1013,
                        "humidity": 65,
                    },
                    "weather": [
                        {
                            "id": 800 + (i % 4),
                            "main": "Clouds" if i % 2 == 0 else "Clear",
                            "description": "scattered clouds" if i % 2 == 0 else "clear sky",
                            "icon": "03d" if i % 2 == 0 else "01d",
                        }
                    ],
                    "dt_txt": datetime.fromtimestamp(dt, tz=UTC).strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return {
            "cod": "200",
            "message": 0,
            "cnt": len(intervals),
            "list": intervals,
            "city": {
                "id": 2643743,
                "name": city_name,
                "coord": {"lat": lat, "lon": lon},
                "country": country,
                "population": 1000000,
                "timezone": timezone_offset,
                "sunrise": start_timestamp,
                "sunset": start_timestamp + 43200,
            },
        }

    return _generate
