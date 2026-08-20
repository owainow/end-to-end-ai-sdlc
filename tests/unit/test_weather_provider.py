"""Unit tests for OpenWeatherMapProvider."""

from typing import Any

import pytest

from src.domain.value_objects import UnitSystem
from src.infrastructure.weather_provider import OpenWeatherMapClient


class TestOpenWeatherMapClientParsing:
    """Tests for OpenWeatherMap response parsing."""

    @pytest.fixture
    def client(self) -> OpenWeatherMapClient:
        """Create client instance."""
        return OpenWeatherMapClient(api_key="test_api_key")

    def test_parse_response_with_country(
        self, client: OpenWeatherMapClient, openweathermap_response: dict[str, Any]
    ) -> None:
        """Test parsing valid response with country."""
        weather_data = client._parse_response(openweathermap_response, UnitSystem.METRIC)
        assert weather_data.city_name == "London"
        assert weather_data.country == "GB"
        assert weather_data.temperature == 15.2

    def test_parse_response_france_country(
        self, client: OpenWeatherMapClient, openweathermap_response: dict[str, Any]
    ) -> None:
        """Test parsing valid response for France."""
        openweathermap_response["sys"]["country"] = "FR"
        openweathermap_response["name"] = "Paris"
        weather_data = client._parse_response(openweathermap_response, UnitSystem.METRIC)
        assert weather_data.city_name == "Paris"
        assert weather_data.country == "FR"

    def test_parse_response_missing_sys(
        self, client: OpenWeatherMapClient, openweathermap_response: dict[str, Any]
    ) -> None:
        """Test parsing response where sys is None or missing."""
        del openweathermap_response["sys"]
        weather_data = client._parse_response(openweathermap_response, UnitSystem.METRIC)
        assert weather_data.country == ""

    def test_parse_response_sys_none(
        self, client: OpenWeatherMapClient, openweathermap_response: dict[str, Any]
    ) -> None:
        """Test parsing response where sys is explicit None."""
        openweathermap_response["sys"] = None
        weather_data = client._parse_response(openweathermap_response, UnitSystem.METRIC)
        assert weather_data.country == ""

    def test_parse_response_missing_country_field(
        self, client: OpenWeatherMapClient, openweathermap_response: dict[str, Any]
    ) -> None:
        """Test parsing response where country field in sys is missing or None."""
        openweathermap_response["sys"] = {}
        weather_data = client._parse_response(openweathermap_response, UnitSystem.METRIC)
        assert weather_data.country == ""
