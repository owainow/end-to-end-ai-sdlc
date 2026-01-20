"""Health check router."""

from fastapi import APIRouter

from src.infrastructure.config import get_settings
from src.presentation.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API is healthy and running.",
)
async def health_check() -> HealthResponse:
    """Return health status of the API.

    Returns:
        HealthResponse with status, version, and environment.
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        environment=settings.environment,
    )
