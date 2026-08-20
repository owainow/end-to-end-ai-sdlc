"""Request logging middleware."""

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.presentation.dependencies import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all incoming requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Log request and response details.

        Args:
            request: The incoming request.
            call_next: The next middleware/handler.

        Returns:
            The response from the handler.
        """
        correlation_id = (
            request.headers.get("x-correlation-id") or f"req-{uuid.uuid4()}"
        )
        request.state.correlation_id = correlation_id

        logger = get_logger()
        start_time = time.perf_counter()

        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else "unknown",
            correlation_id=correlation_id,
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                correlation_id=correlation_id,
            )

            # Add timing and correlation headers
            response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))
            response.headers["x-correlation-id"] = correlation_id
            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
                correlation_id=correlation_id,
            )
            raise
