"""In-memory TTL cache implementation."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock

from src.application.interfaces import CachePort
from src.domain.entities import WeatherData


@dataclass
class CacheEntry:
    """Cache entry with expiration time."""

    value: WeatherData
    expires_at: datetime


class InMemoryCache(CachePort):
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self) -> None:
        """Initialize the cache."""
        self._store: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> WeatherData | None:
        """Retrieve cached weather data if not expired.

        Args:
            key: The cache key.

        Returns:
            Cached WeatherData or None if not found/expired.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            if datetime.now(UTC) > entry.expires_at:
                # Entry expired, remove it
                del self._store[key]
                return None

            return entry.value

    def set(self, key: str, value: WeatherData, ttl_seconds: int) -> None:
        """Store weather data with TTL.

        Args:
            key: The cache key.
            value: The WeatherData to cache.
            ttl_seconds: Time-to-live in seconds.
        """
        with self._lock:
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
            self._store[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> None:
        """Remove an entry from cache.

        Args:
            key: The cache key to delete.
        """
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._store.clear()

    def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed.
        """
        with self._lock:
            now = datetime.now(UTC)
            expired_keys = [
                key for key, entry in self._store.items() if now > entry.expires_at
            ]
            for key in expired_keys:
                del self._store[key]
            return len(expired_keys)

    @property
    def size(self) -> int:
        """Return the number of entries in cache."""
        with self._lock:
            return len(self._store)
