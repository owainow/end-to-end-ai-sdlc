"""Weather API router."""

from fastapi import APIRouter, Depends, Query

from src.application.use_cases import GetWeatherUseCase
from src.domain.entities import WeatherRequest
from src.domain.value_objects import UnitSystem
from src.presentation.dependencies import get_weather_use_case
from src.presentation.schemas import WeatherResponse

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get(
    "",
    response_model=WeatherResponse,
    summary="Get current weather",
    description="Retrieve current weather data for a specified city.",
    responses={
        200: {"description": "Weather data retrieved successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "City not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)
async def get_weather(
    city: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="City name to get weather for",
        examples=["London", "New York", "Tokyo"],
    ),
    units: UnitSystem = Query(
        default=UnitSystem.METRIC,
        description="Temperature units: metric (Celsius) or imperial (Fahrenheit)",
    ),
    use_case: GetWeatherUseCase = Depends(get_weather_use_case),
) -> WeatherResponse:
    """Get current weather for a city.

    Args:
        city: The city name to query.
        units: The temperature unit system.
        use_case: Injected GetWeatherUseCase.

    Returns:
        WeatherResponse with current conditions.
    """
    request = WeatherRequest(city=city, units=units)
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
        units=weather_data.units,
        timestamp=weather_data.timestamp,
    )
