# Research: Real-Time City Weather

**Feature Branch**: `001-realtime-city-weather`  
**Date**: 2026-01-19

## External Weather Provider

### Decision: OpenWeatherMap API

**Rationale**:
- Industry-standard weather API with reliable uptime
- Free tier available for development (1,000 calls/day)
- Supports city name search with fuzzy matching
- Returns all required data: temperature, humidity, wind, pressure, visibility, feels-like
- Supports metric/imperial units natively via `units` parameter
- Well-documented REST API with JSON responses

**Alternatives Considered**:

| Provider | Pros | Cons | Decision |
|----------|------|------|----------|
| OpenWeatherMap | Free tier, comprehensive data, good docs | Rate limits on free tier | ✅ Selected |
| WeatherAPI | Good free tier, 7-day history | Less established | Rejected |
| Tomorrow.io | High accuracy | No free tier for production | Rejected |
| AccuWeather | Trusted brand | Limited free tier (50 calls/day) | Rejected |

**API Endpoint**: `https://api.openweathermap.org/data/2.5/weather`

**Required Parameters**:
- `q` - City name (supports "city", "city,country", "city,state,country")
- `appid` - API key
- `units` - "metric" (Celsius) or "imperial" (Fahrenheit)

**Response Fields Mapping**:

| Spec Entity | API Field |
|-------------|-----------|
| temperature | `main.temp` |
| feels_like | `main.feels_like` |
| humidity | `main.humidity` |
| pressure | `main.pressure` |
| wind_speed | `wind.speed` |
| visibility | `visibility` |
| description | `weather[0].description` |
| city_name | `name` |
| country | `sys.country` |
| coordinates | `coord.lat`, `coord.lon` |

---

## Caching Strategy

### Decision: In-Memory TTL Cache with httpx

**Rationale**:
- Simple implementation for MVP
- No additional infrastructure required
- 15-minute TTL aligns with spec requirement (NFR-004)
- Cache key: `{city_name_normalized}:{units}`
- Fallback: Serve stale cache up to 15 minutes during provider outage

**Implementation Pattern**:
```
CacheEntry = { data: WeatherData, timestamp: datetime, ttl: 900 }
```

**Alternatives Considered**:

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| In-memory dict + TTL | Simple, no dependencies | Lost on restart | ✅ Selected for MVP |
| Redis | Persistent, distributed | Extra infrastructure | Future enhancement |
| File-based | Survives restart | Slow, complex | Rejected |

---

## HTTP Client

### Decision: httpx (async)

**Rationale**:
- Native async support (FastAPI is async)
- Modern Python HTTP client
- Built-in timeout and retry support
- Connection pooling for performance

**Configuration**:
- Timeout: 10 seconds (leaves headroom for <3s p95)
- Retries: 1 retry on connection error
- Connection pool: 10 connections

---

## Error Handling Strategy

### Decision: Domain Exceptions with HTTP Mapping

**Rationale**:
- Clean separation between domain errors and HTTP responses
- Consistent error response format across all endpoints
- Easy to extend for new error types

**Exception Mapping**:

| Domain Exception | HTTP Status | Error Code |
|-----------------|-------------|------------|
| CityNotFoundError | 404 | CITY_NOT_FOUND |
| WeatherProviderUnavailableError | 503 | PROVIDER_UNAVAILABLE |
| RateLimitExceededError | 429 | RATE_LIMITED |
| ValidationError | 400 | VALIDATION_ERROR |
| StaleDataError | 503 | DATA_STALE |

**Error Response Schema**:
```json
{
  "error": {
    "code": "CITY_NOT_FOUND",
    "message": "City 'Xyzabc123' was not found",
    "retry_after": null
  }
}
```

---

## Logging & Metrics

### Decision: Structlog + Prometheus Metrics

**Rationale**:
- Structlog: JSON-formatted logs, easy Azure Log Analytics integration
- Prometheus metrics: Industry standard, Azure Monitor compatible
- FastAPI middleware for automatic request logging

**Log Fields (per request)**:
- `request_id`: UUID
- `method`: HTTP method
- `path`: Request path
- `status_code`: Response status
- `duration_ms`: Request duration
- `city`: Requested city (if applicable)
- `cache_hit`: Boolean

**Metrics**:
- `weather_requests_total{status, cache_hit}` - Counter
- `weather_request_duration_seconds` - Histogram
- `weather_provider_errors_total{error_type}` - Counter

---

## Azure Deployment Considerations

### Decision: Azure App Service (initial), Container Apps (scale)

**Rationale**:
- App Service: Simple deployment, integrated logging, auto-scaling
- Container Apps: Future migration path for container-based deployment
- Environment variables for all configuration (API keys, settings)

**Environment Variables**:
- `OPENWEATHERMAP_API_KEY`: Weather provider API key
- `CACHE_TTL_SECONDS`: Cache TTL (default: 900)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ENVIRONMENT`: dev/staging/production

---

## Summary

All technical unknowns have been resolved:

| Unknown | Resolution |
|---------|------------|
| Weather provider | OpenWeatherMap API |
| Caching | In-memory TTL (15 min) |
| HTTP client | httpx async |
| Error handling | Domain exceptions → HTTP mapping |
| Logging | Structlog JSON |
| Metrics | Prometheus-style counters/histograms |
| Deployment | Azure App Service |

**Next Step**: Phase 1 - Data Model and API Contracts
