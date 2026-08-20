"""Integration tests for the 5-day weather forecast API endpoint."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.entities import DailyForecast, ForecastData
from src.domain.exceptions import (
    CityNotFoundError,
    RateLimitExceededError,
    WeatherProviderError,
)
from src.domain.value_objects import Coordinates, UnitSystem, WeatherCondition


@pytest.fixture
def sample_forecast_data() -> ForecastData:
    """Create sample forecast data for mocking."""
    return ForecastData(
        city_name="London",
        country="GB",
        coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
        units=UnitSystem.METRIC,
        daily_forecasts=[
            DailyForecast(
                date="2026-08-19",
                temp_min=14.0,
                temp_max=22.5,
                condition="clear sky",
                icon_code="01d",
                condition_code=WeatherCondition.CLEAR,
            ),
            DailyForecast(
                date="2026-08-20",
                temp_min=15.0,
                temp_max=23.0,
                condition="few clouds",
                icon_code="02d",
                condition_code=WeatherCondition.CLOUDS,
            ),
            DailyForecast(
                date="2026-08-21",
                temp_min=13.5,
                temp_max=20.0,
                condition="light rain",
                icon_code="10d",
                condition_code=WeatherCondition.RAIN,
            ),
            DailyForecast(
                date="2026-08-22",
                temp_min=12.0,
                temp_max=19.5,
                condition="scattered clouds",
                icon_code="03d",
                condition_code=WeatherCondition.CLOUDS,
            ),
            DailyForecast(
                date="2026-08-23",
                temp_min=14.5,
                temp_max=21.0,
                condition="clear sky",
                icon_code="01d",
                condition_code=WeatherCondition.CLEAR,
            ),
        ],
        timestamp=datetime.now(UTC),
    )


class TestForecastEndpoint:
    """Tests for GET /api/v1/weather/{city}/forecast endpoint."""

    @pytest.mark.asyncio
    async def test_get_forecast_success(self, sample_forecast_data: ForecastData) -> None:
        """Test successful 5-day forecast retrieval with contract validation."""
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(return_value=sample_forecast_data)

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_forecast_use_case

            app = create_app()
            app.dependency_overrides[get_forecast_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/weather/London/forecast")

                assert response.status_code == 200
                data = response.json()

                # Verify top-level structure
                assert data["city"] == "London"
                assert data["country"] == "GB"
                assert data["coordinates"] == {"latitude": 51.5074, "longitude": -0.1278}
                assert data["units"] == "metric"
                assert "timestamp" in data

                # Verify exactly 5 daily forecasts
                assert len(data["daily_forecasts"]) == 5
                first_day = data["daily_forecasts"][0]
                assert first_day["date"] == "2026-08-19"
                assert first_day["temp_min"] == 14.0
                assert first_day["temp_max"] == 22.5
                assert first_day["condition"] == "clear sky"
                assert first_day["condition_code"] == "clear"
                assert first_day["icon_code"] == "01d"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_forecast_with_imperial_units(
        self, sample_forecast_data: ForecastData
    ) -> None:
        """Test 5-day forecast retrieval with imperial units query parameter."""
        imperial_forecast = ForecastData(
            city_name="London",
            country="GB",
            coordinates=sample_forecast_data.coordinates,
            units=UnitSystem.IMPERIAL,
            daily_forecasts=sample_forecast_data.daily_forecasts,
            timestamp=sample_forecast_data.timestamp,
        )
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(return_value=imperial_forecast)

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_forecast_use_case

            app = create_app()
            app.dependency_overrides[get_forecast_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/weather/London/forecast?units=imperial")

                assert response.status_code == 200
                data = response.json()
                assert data["units"] == "imperial"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_forecast_whitespace_city_returns_400(self) -> None:
        """Test whitespace city name returns 400 with INVALID_CITY_NAME code."""
        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/weather/%20%20%20/forecast")

                assert response.status_code == 400
                data = response.json()
                assert "error" in data
                assert data["error"]["code"] == "INVALID_CITY_NAME"
                assert "cannot be empty or whitespace" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_forecast_long_city_returns_validation_error(self) -> None:
        """Test city name exceeding 100 characters returns error."""
        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(f"/api/v1/weather/{'a' * 101}/forecast")

                # FastAPI path validation returns 422
                assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_forecast_city_not_found(self) -> None:
        """Test city not found returns 404 with CITY_NOT_FOUND code."""
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(side_effect=CityNotFoundError("NonExistentCity"))

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_forecast_use_case

            app = create_app()
            app.dependency_overrides[get_forecast_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/weather/NonExistentCity/forecast")

                assert response.status_code == 404
                data = response.json()
                assert data["error"]["code"] == "CITY_NOT_FOUND"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_forecast_rate_limit_exceeded(self) -> None:
        """Test rate limit exceeded returns 429 with Retry-After header and body."""
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=RateLimitExceededError(retry_after_seconds=45)
        )

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_forecast_use_case

            app = create_app()
            app.dependency_overrides[get_forecast_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/weather/London/forecast")

                assert response.status_code == 429
                assert response.headers.get("Retry-After") == "45"
                data = response.json()
                assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
                assert data["error"]["retry_after"] == 45

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_forecast_provider_error(self) -> None:
        """Test provider error returns 502 with PROVIDER_ERROR code and 30s retry_after."""
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(side_effect=WeatherProviderError("OWM API down"))

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_forecast_use_case

            app = create_app()
            app.dependency_overrides[get_forecast_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/weather/London/forecast")

                assert response.status_code == 502
                data = response.json()
                assert data["error"]["code"] == "PROVIDER_ERROR"
                assert data["error"]["retry_after"] == 30

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_forecast_invalid_units(self) -> None:
        """Test forecast request with invalid units parameter returns 422."""
        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/weather/London/forecast?units=kelvin")

                assert response.status_code == 422
