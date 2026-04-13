"""Unit tests for the GetForecastUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.get_forecast import GetForecastUseCase
from src.domain.entities import ForecastData, ForecastDay, WeatherRequest
from src.domain.exceptions import CityNotFoundError
from src.domain.value_objects import Coordinates, UnitSystem


class TestGetForecastUseCase:
    """Tests for GetForecastUseCase."""

    @pytest.fixture
    def mock_provider(self) -> MagicMock:
        """Create a mock forecast provider."""
        provider = MagicMock()
        provider.get_forecast = AsyncMock()
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
    def forecast_data(self) -> ForecastData:
        """Create sample forecast data."""
        days = [
            ForecastDay(
                date="2024-01-19",
                day_label="Today",
                temp_high=16.0,
                temp_low=10.0,
                humidity=70,
                wind_speed=4.5,
                description="scattered clouds",
                icon_code="03d",
                units=UnitSystem.METRIC,
            )
        ]
        return ForecastData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            days=days,
            units=UnitSystem.METRIC,
            timestamp=datetime.now(UTC),
        )

    @pytest.fixture
    def use_case(
        self, mock_provider: MagicMock, mock_cache: MagicMock, mock_logger: MagicMock
    ) -> GetForecastUseCase:
        """Create use case with mocked dependencies."""
        return GetForecastUseCase(
            forecast_provider=mock_provider,
            cache=mock_cache,
            logger=mock_logger,
            cache_ttl_seconds=1800,
        )

    @pytest.mark.asyncio
    async def test_execute_cache_miss(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
        forecast_data: ForecastData,
    ) -> None:
        """Test execution with cache miss fetches from provider."""
        mock_cache.get.return_value = None
        mock_provider.get_forecast.return_value = forecast_data

        request = WeatherRequest(city="London")
        result = await use_case.execute(request)

        assert result.city_name == "London"
        assert len(result.days) == 1
        mock_provider.get_forecast.assert_called_once_with(request)
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_cache_hit(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
        forecast_data: ForecastData,
    ) -> None:
        """Test execution with cache hit skips provider."""
        mock_cache.get.return_value = forecast_data

        request = WeatherRequest(city="London")
        result = await use_case.execute(request)

        assert result.city_name == "London"
        mock_provider.get_forecast.assert_not_called()
        mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_city_not_found(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        """Test execution when city is not found."""
        mock_cache.get.return_value = None
        mock_provider.get_forecast.side_effect = CityNotFoundError("InvalidCity")

        request = WeatherRequest(city="InvalidCity")

        with pytest.raises(CityNotFoundError) as exc_info:
            await use_case.execute(request)

        assert exc_info.value.city == "InvalidCity"
        mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_forecast_cache_key_uses_forecast_prefix(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
        forecast_data: ForecastData,
    ) -> None:
        """Test that forecast cache key starts with 'forecast:' prefix."""
        mock_cache.get.return_value = None
        mock_provider.get_forecast.return_value = forecast_data

        request = WeatherRequest(city="London")
        await use_case.execute(request)

        cache_key_used = mock_cache.get.call_args[0][0]
        assert cache_key_used.startswith("forecast:")
