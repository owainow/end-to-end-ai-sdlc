"""Weather API router."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.application.use_cases import GetForecastUseCase, GetWeatherUseCase
from src.domain.entities import ForecastRequest, WeatherRequest
from src.domain.value_objects import Coordinates, UnitSystem
from src.presentation.dependencies import (
    get_forecast_use_case,
    get_weather_use_case,
)
from src.presentation.schemas import (
    DailyForecastResponse,
    ForecastResponse,
    WeatherResponse,
)

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get(
    "",
    response_model=WeatherResponse,
    summary="Get current weather",
    description="Retrieve current weather data for a specified city or coordinates.",
    responses={
        200: {"description": "Weather data retrieved successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "City not found"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)
async def get_weather(
    city: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="City name to get weather for",
        examples=["London", "New York", "Tokyo"],
    ),
    lat: float | None = Query(
        default=None,
        ge=-90,
        le=90,
        description="Latitude coordinate (must be provided with lon)",
    ),
    lon: float | None = Query(
        default=None,
        ge=-180,
        le=180,
        description="Longitude coordinate (must be provided with lat)",
    ),
    units: UnitSystem = Query(
        default=UnitSystem.METRIC,
        description="Temperature units: metric (Celsius) or imperial (Fahrenheit)",
    ),
    use_case: GetWeatherUseCase = Depends(get_weather_use_case),
) -> WeatherResponse:
    """Get current weather for a city or coordinates.

    Args:
        city: The city name to query.
        lat: Latitude coordinate.
        lon: Longitude coordinate.
        units: The temperature unit system.
        use_case: Injected GetWeatherUseCase.

    Returns:
        WeatherResponse with current conditions.

    Raises:
        HTTPException: If validation fails or coordinates are incomplete.
    """
    # Validate coordinate parameters
    if (lat is None) != (lon is None):
        raise HTTPException(
            status_code=422,
            detail="Both lat and lon must be provided together, or neither",
        )

    # Prefer coordinates over city if both provided
    coordinates = None
    if lat is not None and lon is not None:
        try:
            coordinates = Coordinates(latitude=lat, longitude=lon)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    # Require either coordinates or city
    if not coordinates and not city:
        raise HTTPException(
            status_code=422,
            detail="Either city or coordinates (lat and lon) must be provided",
        )

    # Create request with coordinates or city
    request = WeatherRequest(city=city or "", units=units, coordinates=coordinates)
    weather_data = await use_case.execute(request)

    return WeatherResponse(
        city=weather_data.city_name,
        country=weather_data.country,
        coordinates={
            "latitude": weather_data.coordinates.latitude,
            "longitude": weather_data.coordinates.longitude,
        },
        temperature=weather_data.temperature,
        feels_like=weather_data.feels_like,
        humidity=weather_data.humidity,
        wind_speed=weather_data.wind_speed,
        pressure=weather_data.pressure,
        visibility=weather_data.visibility,
        description=weather_data.description,
        icon_code=weather_data.icon_code,
        units=weather_data.units,
        timestamp=weather_data.timestamp,
    )


@router.get(
    "/{city}/forecast",
    response_model=ForecastResponse,
    summary="Get 5-day weather forecast",
    description="Retrieve 5-day daily weather forecast with high/low temperatures and conditions for a specified city.",
    responses={
        200: {"description": "5-day forecast retrieved successfully"},
        400: {"description": "Invalid city name"},
        404: {"description": "City not found"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
        502: {"description": "Weather provider error"},
        500: {"description": "Internal server error"},
    },
)
async def get_forecast(
    city: str = Path(
        ...,
        min_length=1,
        max_length=100,
        description="City name to get 5-day forecast for",
        examples=["London", "Paris", "Tokyo"],
    ),
    units: UnitSystem = Query(
        default=UnitSystem.METRIC,
        description="Temperature units: metric (Celsius) or imperial (Fahrenheit)",
    ),
    use_case: GetForecastUseCase = Depends(get_forecast_use_case),
) -> ForecastResponse:
    """Get 5-day daily weather forecast for a city.

    Args:
        city: City name path parameter.
        units: Temperature unit system query parameter.
        use_case: Injected GetForecastUseCase.

    Returns:
        ForecastResponse with 5 consecutive daily forecasts.
    """
    request = ForecastRequest(city=city, units=units)
    forecast_data = await use_case.execute(request)

    return ForecastResponse(
        city=forecast_data.city_name,
        country=forecast_data.country,
        coordinates={
            "latitude": forecast_data.coordinates.latitude,
            "longitude": forecast_data.coordinates.longitude,
        },
        units=forecast_data.units,
        daily_forecasts=[
            DailyForecastResponse(
                date=df.date,
                temp_min=df.temp_min,
                temp_max=df.temp_max,
                condition=df.condition,
                icon_code=df.icon_code,
            )
            for df in forecast_data.daily_forecasts
        ],
        timestamp=forecast_data.timestamp,
    )
