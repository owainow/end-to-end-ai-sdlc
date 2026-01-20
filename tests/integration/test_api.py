"""Integration tests for the weather API endpoint."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.entities import WeatherData
from src.domain.value_objects import Coordinates, UnitSystem


@pytest.fixture
def sample_weather_data() -> WeatherData:
    """Create sample weather data for mocking."""
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
        units=UnitSystem.METRIC,
        timestamp=datetime.now(UTC),
    )


@pytest.fixture
async def test_client():
    """Create async test client with mocked settings."""
    with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
        from src.main import create_app

        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


class TestHealthEndpoint:
    """Tests for the health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, test_client: AsyncClient) -> None:
        """Test health endpoint returns healthy status."""
        response = await test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data


class TestWeatherEndpoint:
    """Tests for the weather endpoint."""

    @pytest.mark.asyncio
    async def test_get_weather_success(
        self, sample_weather_data: WeatherData
    ) -> None:
        """Test successful weather retrieval."""
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(return_value=sample_weather_data)

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_weather_use_case

            app = create_app()
            app.dependency_overrides[get_weather_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/api/v1/weather?city=London")

                assert response.status_code == 200
                data = response.json()
                assert data["city"] == "London"
                assert data["country"] == "GB"
                assert data["temperature"] == 15.2

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weather_with_units(
        self, sample_weather_data: WeatherData
    ) -> None:
        """Test weather retrieval with imperial units."""
        imperial_data = WeatherData(
            city_name="London",
            country="GB",
            coordinates=sample_weather_data.coordinates,
            temperature=59.4,
            feels_like=58.6,
            humidity=72,
            wind_speed=10.1,
            pressure=1013,
            visibility=10000,
            description="scattered clouds",
            units=UnitSystem.IMPERIAL,
            timestamp=datetime.now(UTC),
        )

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(return_value=imperial_data)

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_weather_use_case

            app = create_app()
            app.dependency_overrides[get_weather_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/v1/weather?city=London&units=imperial"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["units"] == "imperial"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weather_missing_city(self, test_client: AsyncClient) -> None:
        """Test weather request without city parameter."""
        response = await test_client.get("/api/v1/weather")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_weather_empty_city(self, test_client: AsyncClient) -> None:
        """Test weather request with empty city."""
        response = await test_client.get("/api/v1/weather?city=")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_weather_city_not_found(self) -> None:
        """Test weather request for non-existent city."""
        from src.domain.exceptions import CityNotFoundError

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=CityNotFoundError("InvalidCity123")
        )

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_weather_use_case

            app = create_app()
            app.dependency_overrides[get_weather_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/v1/weather?city=InvalidCity123"
                )

                assert response.status_code == 404
                data = response.json()
                assert data["error"]["code"] == "CITY_NOT_FOUND"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weather_rate_limited(self) -> None:
        """Test rate limit exceeded response."""
        from src.domain.exceptions import RateLimitExceededError

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=RateLimitExceededError(retry_after_seconds=60)
        )

        with patch.dict("os.environ", {"OPENWEATHERMAP_API_KEY": "test_key"}):
            from src.main import create_app
            from src.presentation.dependencies import get_weather_use_case

            app = create_app()
            app.dependency_overrides[get_weather_use_case] = lambda: mock_use_case

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/api/v1/weather?city=London")

                assert response.status_code == 429
                data = response.json()
                assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
                assert data["error"]["retry_after"] == 60
                assert response.headers.get("Retry-After") == "60"

            app.dependency_overrides.clear()
