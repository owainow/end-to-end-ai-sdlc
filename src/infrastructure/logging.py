"""Structured logging adapter using structlog."""

import logging
from typing import Any

import structlog

from src.application.interfaces import LoggerPort

# Map string log levels to logging constants
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def configure_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """Configure structlog for the application.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR).
        json_format: Whether to output JSON formatted logs.
    """
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    numeric_level = LOG_LEVEL_MAP.get(log_level.upper(), logging.INFO)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


class StructlogAdapter(LoggerPort):
    """Structlog adapter implementing LoggerPort."""

    def __init__(self, name: str = "weatherapp") -> None:
        """Initialize the logger.

        Args:
            name: Logger name for context.
        """
        self._logger = structlog.get_logger(name)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self._logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self._logger.debug(message, **kwargs)
