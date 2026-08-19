"""Unit tests for GetForecastUseCase."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.get_forecast import GetForecastUseCase
from src.domain.entities import (
    ForecastData,
    ForecastRequest,
    RawForecastData,
    RawForecastInterval,
)
from src.domain.exceptions import (
    CityNotFoundError,
    RateLimitExceededError,
    WeatherProviderError,
)
from src.domain.value_objects import Coordinates, UnitSystem


@pytest.fixture
def mock_provider() -> MagicMock:
    """Mock weather provider."""
    from src.application.interfaces import WeatherProviderPort

    provider = MagicMock(spec=WeatherProviderPort)
    provider.get_forecast_raw = AsyncMock()
    return provider


@pytest.fixture
def mock_cache() -> MagicMock:
    """Mock cache."""
    from src.application.interfaces import CachePort

    cache = MagicMock(spec=CachePort)
    cache.get = MagicMock(return_value=None)
    cache.set = MagicMock()
    return cache


@pytest.fixture
def mock_logger() -> MagicMock:
    """Mock logger."""
    from src.application.interfaces import LoggerPort

    logger = MagicMock(spec=LoggerPort)
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    return logger


@pytest.fixture
def use_case(
    mock_provider: MagicMock,
    mock_cache: MagicMock,
    mock_logger: MagicMock,
) -> GetForecastUseCase:
    """Create GetForecastUseCase instance with mocks."""
    return GetForecastUseCase(
        weather_provider=mock_provider,
        cache=mock_cache,
        logger=mock_logger,
        cache_ttl_seconds=900,
    )


def create_raw_intervals(
    start_timestamp: int,
    count: int = 40,
    interval_hours: int = 3,
    base_temp: float = 20.0,
) -> list[RawForecastInterval]:
    """Helper to generate sequential raw forecast intervals."""
    intervals: list[RawForecastInterval] = []
    for i in range(count):
        dt = datetime.fromtimestamp(start_timestamp + i * interval_hours * 3600, tz=UTC)
        temp = base_temp + (i % 8) * 1.5 - (i % 4) * 0.5
        intervals.append(
            RawForecastInterval(
                dt=dt,
                temp=round(temp, 1),
                condition="clear sky" if i % 2 == 0 else "scattered clouds",
                icon_code="01d" if i % 2 == 0 else "03d",
            )
        )
    return intervals


class TestGetForecastUseCase:
    """Tests for GetForecastUseCase."""

    @pytest.mark.asyncio
    async def test_execute_cache_miss_aggregates_5_days(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        """Test cache miss fetches raw forecast, aggregates 5 days, and caches result."""
        # Start at 2026-08-19 00:00:00 UTC (timestamp 1787097600)
        start_ts = 1787097600
        raw_intervals = create_raw_intervals(start_ts, count=40)
        raw_data = RawForecastData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            timezone_offset=0,
            intervals=raw_intervals,
        )
        mock_provider.get_forecast_raw.return_value = raw_data

        request = ForecastRequest(city="London", units=UnitSystem.METRIC)
        result = await use_case.execute(request)

        assert isinstance(result, ForecastData)
        assert result.city_name == "London"
        assert result.country == "GB"
        assert len(result.daily_forecasts) == 5

        # Check dates are consecutive
        expected_dates = [
            "2026-08-19",
            "2026-08-20",
            "2026-08-21",
            "2026-08-22",
            "2026-08-23",
        ]
        assert [df.date for df in result.daily_forecasts] == expected_dates

        # Verify caching
        mock_cache.get.assert_called_once_with("forecast:london:metric")
        mock_cache.set.assert_called_once_with("forecast:london:metric", result, 900)
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_cache_hit_returns_cached_data(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
        mock_cache: MagicMock,
        mock_logger: MagicMock,
        sample_forecast_data: ForecastData,
    ) -> None:
        """Test cache hit returns cached ForecastData immediately without calling provider."""
        mock_cache.get.return_value = sample_forecast_data

        request = ForecastRequest(city="London", units=UnitSystem.METRIC)
        result = await use_case.execute(request)

        assert result == sample_forecast_data
        mock_provider.get_forecast_raw.assert_not_called()
        mock_cache.set.assert_not_called()
        mock_logger.debug.assert_called_with(
            "Cache hit",
            city="London",
            units="metric",
            cache_key="forecast:london:metric",
        )

    @pytest.mark.asyncio
    async def test_timezone_offset_handling_and_6_calendar_days(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
    ) -> None:
        """Test grouping across 6 calendar days and fractional timezone offset (UTC+5:30)."""
        # Start at 2026-08-19 21:00:00 UTC with timezone offset +19800 (UTC+5:30 -> 2026-08-20 02:30:00)
        # 40 intervals of 3 hours = 120 hours, which will span into 6 distinct local calendar days
        start_ts = 1787173200  # 2026-08-19 21:00:00 UTC
        raw_intervals = create_raw_intervals(start_ts, count=40)
        raw_data = RawForecastData(
            city_name="Mumbai",
            country="IN",
            coordinates=Coordinates(latitude=19.0760, longitude=72.8777),
            timezone_offset=19800,  # +5:30
            intervals=raw_intervals,
        )
        mock_provider.get_forecast_raw.return_value = raw_data

        request = ForecastRequest(city="Mumbai", units=UnitSystem.METRIC)
        result = await use_case.execute(request)

        assert len(result.daily_forecasts) == 5
        # The first local calendar day in UTC+5:30 is 2026-08-20
        assert result.daily_forecasts[0].date == "2026-08-20"
        assert result.daily_forecasts[4].date == "2026-08-24"

    @pytest.mark.asyncio
    async def test_midday_condition_selection_and_equidistant_tie_breaking(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
    ) -> None:
        """Test that midday interval is selected, and ties equidistant from 12:00 select earlier interval."""
        # 5 days of data, on day 1 we explicitly set intervals at 09:00:00 and 15:00:00 (both 3 hours from 12:00:00)
        # 09:00:00 has condition "morning sun" / icon "01d"
        # 15:00:00 has condition "afternoon cloud" / icon "03d"
        # Tie breaker must choose 09:00:00 ("morning sun" / "01d")
        dt_day1_9am = datetime(2026, 8, 19, 9, 0, 0, tzinfo=UTC)
        dt_day1_3pm = datetime(2026, 8, 19, 15, 0, 0, tzinfo=UTC)

        intervals = [
            RawForecastInterval(
                dt=dt_day1_9am, temp=18.0, condition="morning sun", icon_code="01d"
            ),
            RawForecastInterval(
                dt=dt_day1_3pm, temp=24.0, condition="afternoon cloud", icon_code="03d"
            ),
        ]

        # Add days 2, 3, 4, 5
        for day in range(20, 24):
            dt_midday = datetime(2026, 8, day, 12, 0, 0, tzinfo=UTC)
            intervals.append(
                RawForecastInterval(dt=dt_midday, temp=20.0, condition="clear sky", icon_code="01d")
            )

        raw_data = RawForecastData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            timezone_offset=0,
            intervals=intervals,
        )
        mock_provider.get_forecast_raw.return_value = raw_data

        request = ForecastRequest(city="London", units=UnitSystem.METRIC)
        result = await use_case.execute(request)

        assert len(result.daily_forecasts) == 5
        day1 = result.daily_forecasts[0]
        assert day1.date == "2026-08-19"
        assert day1.temp_min == 18.0
        assert day1.temp_max == 24.0
        # Earlier interval won tie-break
        assert day1.condition == "morning sun"
        assert day1.icon_code == "01d"

    @pytest.mark.asyncio
    async def test_insufficient_days_raises_weather_provider_error(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
    ) -> None:
        """Test that provider returning fewer than 5 days raises WeatherProviderError."""
        # Only 3 days of intervals
        intervals = [
            RawForecastInterval(
                dt=datetime(2026, 8, day, 12, 0, 0, tzinfo=UTC),
                temp=20.0,
                condition="clear sky",
                icon_code="01d",
            )
            for day in range(19, 22)
        ]
        raw_data = RawForecastData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            timezone_offset=0,
            intervals=intervals,
        )
        mock_provider.get_forecast_raw.return_value = raw_data

        request = ForecastRequest(city="London", units=UnitSystem.METRIC)
        with pytest.raises(WeatherProviderError, match="Insufficient forecast data"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_units_passed_to_request_and_provider(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
    ) -> None:
        """Test that imperial unit system is passed to provider and preserved in entity."""
        start_ts = 1787097600
        raw_intervals = create_raw_intervals(start_ts, count=40, base_temp=68.0)
        raw_data = RawForecastData(
            city_name="New York",
            country="US",
            coordinates=Coordinates(latitude=40.7128, longitude=-74.006),
            timezone_offset=-14400,  # UTC-4
            intervals=raw_intervals,
        )
        mock_provider.get_forecast_raw.return_value = raw_data

        request = ForecastRequest(city="New York", units=UnitSystem.IMPERIAL)
        result = await use_case.execute(request)

        assert result.units == UnitSystem.IMPERIAL
        mock_provider.get_forecast_raw.assert_called_once_with(
            city="New York", units=UnitSystem.IMPERIAL
        )

    @pytest.mark.asyncio
    async def test_city_not_found_propagates(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
    ) -> None:
        """Test that CityNotFoundError from provider is not suppressed."""
        mock_provider.get_forecast_raw.side_effect = CityNotFoundError("UnknownCity")

        request = ForecastRequest(city="UnknownCity", units=UnitSystem.METRIC)
        with pytest.raises(CityNotFoundError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_propagates(
        self,
        use_case: GetForecastUseCase,
        mock_provider: MagicMock,
    ) -> None:
        """Test that RateLimitExceededError from provider is not suppressed."""
        mock_provider.get_forecast_raw.side_effect = RateLimitExceededError(60)

        request = ForecastRequest(city="London", units=UnitSystem.METRIC)
        with pytest.raises(RateLimitExceededError):
            await use_case.execute(request)
