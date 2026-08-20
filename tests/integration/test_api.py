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
        icon_code="03d",
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
            icon_code="03d",
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
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert data["error"]["message"] == "Either city or coordinates (lat and lon) must be provided"
        assert data["error"]["target"] == "city"
        assert "correlationId" in data["error"]
        assert response.headers.get("x-correlation-id") == data["error"]["correlationId"]
        assert "retryAfter" not in data["error"]
        assert "retry_after" not in data["error"]

    @pytest.mark.asyncio
    async def test_get_weather_empty_city(self, test_client: AsyncClient) -> None:
        """Test weather request with empty city."""
        response = await test_client.get("/api/v1/weather?city=")

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert data["error"]["message"] == "City name cannot be empty"
        assert data["error"]["target"] == "city"
        assert "correlationId" in data["error"]
        assert response.headers.get("x-correlation-id") == data["error"]["correlationId"]
        assert "retryAfter" not in data["error"]
        assert "retry_after" not in data["error"]

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
                assert data["error"]["target"] == "city"

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
                assert data["error"]["code"] == "RATE_LIMITED"
                assert data["error"]["retryAfter"] == 60
                assert "retry_after" not in data["error"]
                assert response.headers.get("Retry-After") == "60"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weather_with_coordinates(
        self, sample_weather_data: WeatherData
    ) -> None:
        """Test weather retrieval with coordinates."""
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
                response = await client.get(
                    "/api/v1/weather?lat=51.5074&lon=-0.1278&units=metric"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["city"] == "London"
                assert data["coordinates"]["latitude"] == 51.5074
                assert data["coordinates"]["longitude"] == -0.1278

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weather_with_lat_only(self, test_client: AsyncClient) -> None:
        """Test weather request with lat only (no lon) returns 422."""
        response = await test_client.get("/api/v1/weather?lat=51.5074")
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert "lat and lon must be provided together" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_weather_with_lon_only(self, test_client: AsyncClient) -> None:
        """Test weather request with lon only (no lat) returns 422."""
        response = await test_client.get("/api/v1/weather?lon=-0.1278")
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert "lat and lon must be provided together" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_weather_with_invalid_lat(
        self, test_client: AsyncClient
    ) -> None:
        """Test weather request with out-of-range lat returns 422."""
        response = await test_client.get("/api/v1/weather?lat=91.0&lon=0.0")
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"

    @pytest.mark.asyncio
    async def test_get_weather_with_invalid_lon(
        self, test_client: AsyncClient
    ) -> None:
        """Test weather request with out-of-range lon returns 422."""
        response = await test_client.get("/api/v1/weather?lat=0.0&lon=181.0")
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"

    @pytest.mark.asyncio
    async def test_get_weather_coords_preferred_over_city(
        self, sample_weather_data: WeatherData
    ) -> None:
        """Test that coordinates are preferred over city when both provided."""
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
                response = await client.get(
                    "/api/v1/weather?city=Paris&lat=51.5074&lon=-0.1278"
                )

                assert response.status_code == 200
                # Verify the use case was called with coordinates
                call_args = mock_use_case.execute.call_args[0][0]
                assert call_args.coordinates is not None
                assert call_args.coordinates.latitude == 51.5074
                assert call_args.coordinates.longitude == -0.1278

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weather_no_city_no_coords(
        self, test_client: AsyncClient
    ) -> None:
        """Test weather request without city or coords returns 422."""
        response = await test_client.get("/api/v1/weather")
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert "Either city or coordinates" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_weather_numeric_city(self, test_client: AsyncClient) -> None:
        """Test weather request with purely numeric city returns 422 with target city."""
        response = await test_client.get("/api/v1/weather?city=12345")
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert data["error"]["target"] == "city"
        assert "must contain letters" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_weather_overlong_city(self, test_client: AsyncClient) -> None:
        """Test weather request with over 100 char city returns 422."""
        long_city = "a" * 101
        response = await test_client.get(f"/api/v1/weather?city={long_city}")
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert data["error"]["target"] == "city"
        assert "must not exceed 100 characters" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_correlation_id_propagation(self, test_client: AsyncClient) -> None:
        """Test that custom x-correlation-id header is preserved in error response."""
        custom_id = "req-custom-correlation-123"
        response = await test_client.get(
            "/api/v1/weather?city=12345",
            headers={"x-correlation-id": custom_id},
        )
        assert response.status_code == 422
        data = response.json()
        assert response.headers.get("x-correlation-id") == custom_id
        assert data["error"]["correlationId"] == custom_id

    @pytest.mark.asyncio
    async def test_generated_correlation_id(self, test_client: AsyncClient) -> None:
        """Test that generated x-correlation-id is returned when none provided."""
        response = await test_client.get("/api/v1/weather?city=12345")
        assert response.status_code == 422
        data = response.json()
        cid = response.headers.get("x-correlation-id")
        assert cid is not None
        assert cid.startswith("req-")
        assert data["error"]["correlationId"] == cid

    @pytest.mark.asyncio
    async def test_dual_params_invalid_city_fails(
        self, test_client: AsyncClient
    ) -> None:
        """Test that providing invalid city alongside valid coords fails on city first."""
        response = await test_client.get(
            "/api/v1/weather?city=12345&lat=51.5074&lon=-0.1278"
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
        assert data["error"]["target"] == "city"
        assert "must contain letters" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_weather_coordinates_not_found(self) -> None:
        """Test 404 for coordinate lookup sets target='coordinates' instead of 'city'."""
        from src.domain.exceptions import CityNotFoundError

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=CityNotFoundError("(0.0000, 0.0000)")
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
                response = await client.get("/api/v1/weather?lat=0.0&lon=0.0")

                assert response.status_code == 404
                data = response.json()
                assert data["error"]["code"] == "CITY_NOT_FOUND"
                assert data["error"]["target"] == "coordinates"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_http_exception_custom_error_code(self) -> None:
        """Test that http_exception_handler preserves explicit error code in detail dict."""
        from fastapi import HTTPException

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_COORDINATES",
                    "message": "Latitude out of range",
                    "target": "coordinates",
                },
            )
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

                assert response.status_code == 422
                data = response.json()
                assert data["error"]["code"] == "INVALID_COORDINATES"
                assert data["error"]["message"] == "Latitude out of range"
                assert data["error"]["target"] == "coordinates"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_weather_dual_params_coordinates_not_found(self) -> None:
        """Test 404 when both city and lat/lon provided sets target='coordinates'."""
        from src.domain.exceptions import CityNotFoundError

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=CityNotFoundError("(0.0000, 0.0000)")
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
                response = await client.get("/api/v1/weather?city=London&lat=0.0&lon=0.0")

                assert response.status_code == 404
                data = response.json()
                assert data["error"]["code"] == "CITY_NOT_FOUND"
                assert data["error"]["target"] == "coordinates"

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_weather_provider_error_returns_503(self) -> None:
        """Test WeatherProviderError yields HTTP 503 with PROVIDER_UNAVAILABLE code."""
        from src.domain.exceptions import WeatherProviderError

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=WeatherProviderError("Connection timeout")
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

                assert response.status_code == 503
                data = response.json()
                assert data["error"]["code"] == "PROVIDER_UNAVAILABLE"
                assert data["error"]["message"] == "Weather service temporarily unavailable"
                assert data["error"]["retryAfter"] == 30

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_openapi_schema_error_responses_linked(self, test_client: AsyncClient) -> None:
        """Test that /openapi.json links ErrorResponse schema for error status codes."""
        response = await test_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        weather_get = schema["paths"]["/api/v1/weather"]["get"]
        responses = weather_get["responses"]

        for status_code in ["400", "404", "422", "429", "500", "503"]:
            assert status_code in responses
            content = responses[status_code]["content"]["application/json"]
            assert "$ref" in content["schema"]
            assert "ErrorResponse" in content["schema"]["$ref"]

    @pytest.mark.asyncio
    async def test_docs_openapi_yaml_exists(self) -> None:
        """Test that /docs/openapi.yaml file exists and is non-empty."""
        from pathlib import Path

        openapi_path = Path("docs/openapi.yaml")
        assert openapi_path.exists()
        assert openapi_path.stat().st_size > 0



