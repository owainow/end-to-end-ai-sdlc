"""Shared test fixtures for Weather App tests."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities import WeatherData
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
        icon_code="03d",
        weather_main="Clouds",
        units=UnitSystem.METRIC,
        timestamp=datetime.now(UTC),
    )


@pytest.fixture
def mock_weather_provider() -> MagicMock:
    """Mock weather provider for testing."""
    from src.application.interfaces import WeatherProviderPort

    provider = MagicMock(spec=WeatherProviderPort)
    provider.get_weather = AsyncMock()
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
