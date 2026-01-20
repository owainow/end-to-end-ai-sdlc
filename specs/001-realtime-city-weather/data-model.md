# Data Model: Real-Time City Weather

**Feature Branch**: `001-realtime-city-weather`  
**Date**: 2026-01-19

## Domain Entities

### WeatherData

Represents current weather conditions for a location.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| city_name | string | Name of the city | Required, non-empty |
| country | string | ISO country code | Required, 2 characters |
| coordinates | Coordinates | Lat/lon of location | Required |
| temperature | float | Current temperature | Required |
| feels_like | float | "Feels like" temperature | Required |
| humidity | int | Humidity percentage | Required, 0-100 |
| wind_speed | float | Wind speed | Required, >= 0 |
| pressure | int | Atmospheric pressure (hPa) | Required, > 0 |
| visibility | int | Visibility in meters | Required, >= 0 |
| description | string | Weather description | Required, non-empty |
| units | UnitSystem | metric or imperial | Required |
| timestamp | datetime | Data retrieval time | Required, UTC |

### Coordinates

Represents geographic coordinates.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| latitude | float | Latitude | Required, -90 to 90 |
| longitude | float | Longitude | Required, -180 to 180 |

### WeatherRequest

Represents a user's request for weather data.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| city | string | City name to search | Required, non-empty, max 100 chars |
| units | UnitSystem | Preferred units | Optional, defaults to "metric" |

### UnitSystem (Enum)

| Value | Description |
|-------|-------------|
| metric | Celsius, m/s |
| imperial | Fahrenheit, mph |

---

## Error Types

### CityNotFoundError

Raised when the requested city cannot be found by the weather provider.

| Field | Type | Description |
|-------|------|-------------|
| city | string | The city that was not found |
| message | string | User-friendly error message |

### WeatherProviderUnavailableError

Raised when the external weather provider is unavailable.

| Field | Type | Description |
|-------|------|-------------|
| message | string | User-friendly error message |
| retry_after | int? | Seconds to wait before retry (optional) |

### RateLimitExceededError

Raised when the weather provider rate limits the request.

| Field | Type | Description |
|-------|------|-------------|
| message | string | User-friendly error message |
| retry_after | int | Seconds to wait before retry |

### StaleDataError

Raised when cached data exceeds the 15-minute threshold.

| Field | Type | Description |
|-------|------|-------------|
| message | string | User-friendly error message |
| last_updated | datetime | When data was last successfully fetched |

---

## Cache Entry

Internal structure for caching weather data.

| Field | Type | Description |
|-------|------|-------------|
| data | WeatherData | Cached weather data |
| fetched_at | datetime | When data was fetched |
| expires_at | datetime | When cache entry expires (fetched_at + 15 min) |

**Cache Key Format**: `weather:{normalized_city}:{units}`

**Normalization**: City name lowercased, whitespace trimmed, diacritics preserved.

---

## Entity Relationships

```
WeatherRequest
    │
    └──▶ GetWeatherUseCase
              │
              ├──▶ Cache (check first)
              │      │
              │      └──▶ CacheEntry ──▶ WeatherData
              │
              └──▶ WeatherProvider (on cache miss)
                     │
                     └──▶ WeatherData
```

---

## State Transitions

### Cache Entry Lifecycle

```
                 ┌─────────────────┐
                 │   NOT_CACHED    │
                 └────────┬────────┘
                          │ fetch success
                          ▼
                 ┌─────────────────┐
        ┌───────▶│     FRESH       │◀───────┐
        │        └────────┬────────┘        │
        │                 │ TTL expires     │
        │                 ▼                 │
        │        ┌─────────────────┐        │
        │        │     STALE       │────────┘
        │        └────────┬────────┘  fetch success
        │                 │ 15 min exceeded
        │                 ▼
        │        ┌─────────────────┐
        └────────│    EXPIRED      │
   fetch success └─────────────────┘
```

**Behavior**:
- FRESH: Serve immediately
- STALE: Serve if provider unavailable, attempt refresh in background
- EXPIRED: Do not serve, return error if provider unavailable
