"""Weather App main entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager.

    Handles startup and shutdown events.
    """
    from src.infrastructure.config import get_settings
    from src.infrastructure.logging import configure_logging

    settings = get_settings()
    configure_logging(
        log_level=settings.log_level,
        json_format=settings.environment != "dev",
    )
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    from src.infrastructure.config import get_settings
    from src.presentation.exception_handlers import register_exception_handlers
    from src.presentation.middleware import RequestLoggingMiddleware
    from src.presentation.routers import health_router, weather_router

    settings = get_settings()

    app = FastAPI(
        title="Weather App API",
        description="Real-time weather data API with caching and unit conversion",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Include routers
    app.include_router(health_router)
    app.include_router(weather_router, prefix=f"/api/{settings.api_version}")

    # Serve static files (must be last, catches all unmatched routes)
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


def get_app() -> FastAPI:
    """Get or create the FastAPI application (lazy loading)."""
    return create_app()


if __name__ == "__main__":
    import uvicorn

    from src.infrastructure.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "src.main:get_app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "dev",
        factory=True,
    )
