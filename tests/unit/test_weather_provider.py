"""Unit tests for OpenWeatherMapClient."""

from typing import Any
from unittest.mock import patch

import httpx
import pytest

from src.domain.entities import RawForecastData
from src.domain.exceptions import (
    CityNotFoundError,
    RateLimitExceededError,
    WeatherProviderError,
)
from src.domain.value_objects import UnitSystem
from src.infrastructure.weather_provider import OpenWeatherMapClient


@pytest.fixture
def client() -> OpenWeatherMapClient:
    """Create OpenWeatherMapClient instance."""
    return OpenWeatherMapClient(
        api_key="test_api_key",
        base_url="https://api.openweathermap.org/data/2.5",
        timeout_seconds=5.0,
    )


class TestOpenWeatherMapClientForecast:
    """Tests for OpenWeatherMapClient.get_forecast_raw."""

    @pytest.mark.asyncio
    async def test_get_forecast_raw_success(
        self, client: OpenWeatherMapClient, make_forecast_payload: Any
    ) -> None:
        """Test successful raw forecast fetching and parsing."""
        payload = make_forecast_payload(
            city_name="London",
            country="GB",
            lat=51.5074,
            lon=-0.1278,
            timezone_offset=0,
            count=40,
        )

        mock_response = httpx.Response(
            status_code=200,
            json=payload,
            request=httpx.Request("GET", "https://api.openweathermap.org/data/2.5/forecast"),
        )

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await client.get_forecast_raw("London", UnitSystem.METRIC)

            assert isinstance(result, RawForecastData)
            assert result.city_name == "London"
            assert result.country == "GB"
            assert result.coordinates.latitude == 51.5074
            assert result.coordinates.longitude == -0.1278
            assert result.timezone_offset == 0
            assert len(result.intervals) == 40
            assert result.intervals[0].condition in ["scattered clouds", "clear sky"]

    @pytest.mark.asyncio
    async def test_get_forecast_raw_city_not_found(self, client: OpenWeatherMapClient) -> None:
        """Test 404 response raises CityNotFoundError."""
        mock_response = httpx.Response(
            status_code=404,
            json={"cod": "404", "message": "city not found"},
            request=httpx.Request("GET", "https://api.openweathermap.org/data/2.5/forecast"),
        )

        with (
            patch("httpx.AsyncClient.get", return_value=mock_response),
            pytest.raises(CityNotFoundError, match="UnknownCity"),
        ):
            await client.get_forecast_raw("UnknownCity", UnitSystem.METRIC)

    @pytest.mark.asyncio
    async def test_get_forecast_raw_rate_limit(self, client: OpenWeatherMapClient) -> None:
        """Test 429 response raises RateLimitExceededError with retry_after."""
        mock_response = httpx.Response(
            status_code=429,
            headers={"Retry-After": "30"},
            json={"cod": 429, "message": "rate limit"},
            request=httpx.Request("GET", "https://api.openweathermap.org/data/2.5/forecast"),
        )

        with (
            patch("httpx.AsyncClient.get", return_value=mock_response),
            pytest.raises(RateLimitExceededError) as exc_info,
        ):
            await client.get_forecast_raw("London", UnitSystem.METRIC)
        assert exc_info.value.retry_after_seconds == 30

    @pytest.mark.asyncio
    async def test_get_forecast_raw_provider_error(self, client: OpenWeatherMapClient) -> None:
        """Test 500 response raises WeatherProviderError."""
        mock_response = httpx.Response(
            status_code=500,
            text="Internal Server Error",
            request=httpx.Request("GET", "https://api.openweathermap.org/data/2.5/forecast"),
        )

        with (
            patch("httpx.AsyncClient.get", return_value=mock_response),
            pytest.raises(WeatherProviderError, match="status 500"),
        ):
            await client.get_forecast_raw("London", UnitSystem.METRIC)

    @pytest.mark.asyncio
    async def test_get_forecast_raw_timeout(self, client: OpenWeatherMapClient) -> None:
        """Test request timeout raises WeatherProviderError."""
        with (
            patch(
                "httpx.AsyncClient.get",
                side_effect=httpx.TimeoutException("Connection timed out"),
            ),
            pytest.raises(WeatherProviderError, match="Request timed out"),
        ):
            await client.get_forecast_raw("London", UnitSystem.METRIC)

    @pytest.mark.asyncio
    async def test_get_forecast_raw_network_error(self, client: OpenWeatherMapClient) -> None:
        """Test network failure raises WeatherProviderError."""
        with (
            patch(
                "httpx.AsyncClient.get",
                side_effect=httpx.RequestError("Network unreachable"),
            ),
            pytest.raises(WeatherProviderError, match="Request failed"),
        ):
            await client.get_forecast_raw("London", UnitSystem.METRIC)
