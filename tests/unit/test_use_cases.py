"""Unit tests for the GetWeatherUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases import GetWeatherUseCase
from src.domain.entities import WeatherData, WeatherRequest
from src.domain.exceptions import CityNotFoundError
from src.domain.value_objects import Coordinates, UnitSystem


class TestGetWeatherUseCase:
    """Tests for GetWeatherUseCase."""

    @pytest.fixture
    def mock_provider(self) -> MagicMock:
        """Create a mock weather provider."""
        provider = MagicMock()
        provider.get_weather = AsyncMock()
        return provider

    @pytest.fixture
    def mock_cache(self) -> MagicMock:
        """Create a mock cache."""
        cache = MagicMock()
        cache.get = MagicMock(return_value=None)
        cache.set = MagicMock()
        return cache

    @pytest.fixture
    def mock_logger(self) -> MagicMock:
        """Create a mock logger."""
        return MagicMock()

    @pytest.fixture
    def weather_data(self) -> WeatherData:
        """Create sample weather data."""
        return WeatherData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            temperature=15.2,
            feels_like=14.8,
            humidity=72,
            wind_speed=4.5,
            pressure=1013,
            visibility=10000,
            description="scattered clouds",
            icon_code="03d",
            units=UnitSystem.METRIC,
            timestamp=datetime.now(UTC),
        )

    @pytest.fixture
    def use_case(
        self, mock_provider: MagicMock, mock_cache: MagicMock, mock_logger: MagicMock
    ) -> GetWeatherUseCase:
        """Create use case with mocked dependencies."""
        return GetWeatherUseCase(
            weather_provider=mock_provider,
            cache=mock_cache,
            logger=mock_logger,
            cache_ttl_seconds=900,
        )

    @pytest.mark.asyncio
    async def test_execute_cache_miss(
        self,
        use_case: GetWeatherUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
        weather_data: WeatherData,
    ) -> None:
        """Test execution with cache miss."""
        mock_cache.get.return_value = None
        mock_provider.get_weather.return_value = weather_data

        request = WeatherRequest(city="London")
        result = await use_case.execute(request)

        assert result.city_name == "London"
        assert result.temperature == 15.2
        mock_provider.get_weather.assert_called_once_with(request)
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_cache_hit(
        self,
        use_case: GetWeatherUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
        weather_data: WeatherData,
    ) -> None:
        """Test execution with cache hit."""
        mock_cache.get.return_value = weather_data

        request = WeatherRequest(city="London")
        result = await use_case.execute(request)

        assert result.city_name == "London"
        mock_provider.get_weather.assert_not_called()
        mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_city_not_found(
        self,
        use_case: GetWeatherUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        """Test execution when city is not found."""
        mock_cache.get.return_value = None
        mock_provider.get_weather.side_effect = CityNotFoundError("InvalidCity")

        request = WeatherRequest(city="InvalidCity")

        with pytest.raises(CityNotFoundError) as exc_info:
            await use_case.execute(request)

        assert exc_info.value.city == "InvalidCity"
        mock_cache.set.assert_not_called()
