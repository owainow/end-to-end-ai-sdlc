# Architecture: Geolocation Button

## Overview
This feature adds geolocation capability to the Weather App, allowing users to get weather for their current location with a single click. The implementation spans frontend (browser Geolocation API) and backend (coordinate-based weather lookup).

## Architecture Decisions

### AD-001: Coordinate-Based Weather API
**Decision**: Add a new backend endpoint that accepts latitude/longitude and returns weather data

**Context**: 
- OpenWeatherMap supports weather lookup by coordinates directly
- This is more reliable than reverse geocoding + city search

**Options Considered**:
1. **Direct coordinate weather lookup** (Selected)
   - Pros: Single API call, more accurate, handles edge cases (rural areas)
   - Cons: New backend endpoint required

2. **Reverse geocode to city, then search**
   - Pros: Reuses existing city search
   - Cons: Two API calls, may fail for locations not near named cities

**Rationale**: Direct coordinate lookup is more reliable and faster (one API call vs two).

### AD-002: Frontend-Only Geolocation
**Decision**: All geolocation logic lives in the frontend JavaScript

**Context**: 
- Browser Geolocation API is client-side only
- Coordinates are sent to backend only for weather lookup

**Rationale**: 
- Geolocation API is a browser feature
- Keeps backend stateless and privacy-focused
- No server-side tracking of user location

### AD-003: Optional Coordinates on Weather Endpoint
**Decision**: Extend existing weather endpoint to accept optional `lat` and `lon` parameters as alternative to `city`

**Options Considered**:
1. **New separate endpoint** `/api/v1/weather/location`
   - Pros: Clear separation
   - Cons: Code duplication, two endpoints to maintain

2. **Extend existing endpoint** (Selected)
   - Pros: DRY, unified response format
   - Cons: Slightly more complex validation

**Rationale**: Single endpoint with flexible input is cleaner and easier to maintain.

## Component Architecture

### Frontend Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Search Section                          │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌──────────┐  ┌────────────────┐   │
│  │   City Input      │  │ Location │  │  Search Btn    │   │
│  │   [text field]    │  │   [📍]   │  │   [Search]     │   │
│  └───────────────────┘  └──────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### State Changes

```javascript
// New state properties
state = {
    // ... existing
    geolocating: false,        // true while detecting location
    geolocationError: null     // error message if geolocation fails
}
```

### API Flow

```
┌──────────┐     ┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
│  User    │────▶│ Browser GeoAPI  │────▶│  Frontend   │────▶│   Backend   │
│  clicks  │     │ getCurrentPos() │     │ sends coords│     │ /weather    │
└──────────┘     └─────────────────┘     └─────────────┘     └─────────────┘
                         │                      │                    │
                         ▼                      │                    ▼
                  ┌──────────────┐              │           ┌─────────────┐
                  │ lat, lon     │──────────────┘           │ OpenWeather │
                  │ coordinates  │                          │ API (coord) │
                  └──────────────┘                          └─────────────┘
```

## File Changes

### Backend Files

| File | Change Type | Description |
|------|-------------|-------------|
| `src/presentation/routers/weather.py` | Modify | Add optional `lat`, `lon` query params |
| `src/application/weather_service.py` | Modify | Add `get_weather_by_coordinates()` method |
| `src/infrastructure/weather_client.py` | Modify | Add coordinate-based API call |
| `src/presentation/schemas.py` | Modify | Update request validation for coords |

### Frontend Files

| File | Change Type | Description |
|------|-------------|-------------|
| `static/index.html` | Modify | Add geolocation button, JS handlers, error UI |

### Test Files

| File | Change Type | Description |
|------|-------------|-------------|
| `tests/unit/test_weather_service.py` | Modify | Add coordinate-based tests |
| `tests/unit/test_weather_router.py` | Modify | Add endpoint tests with coords |
| `tests/integration/test_weather_api.py` | Modify | Add integration tests |

## API Specification

### Extended Weather Endpoint

```
GET /api/v1/weather
```

**Query Parameters** (mutually exclusive options):

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| city | string | No* | City name |
| lat | float | No* | Latitude (-90 to 90) |
| lon | float | No* | Longitude (-180 to 180) |
| units | string | No | "metric" or "imperial" |

*Either `city` OR both `lat` and `lon` required

**Validation**:
- If `lat` provided, `lon` must also be provided (and vice versa)
- If both `city` and coords provided, coords take precedence
- Latitude range: -90 to 90
- Longitude range: -180 to 180

**Response**: Same as existing weather response (includes city name from reverse lookup)

## Error Handling

### Frontend Geolocation Errors

| Error Code | User Message |
|------------|--------------|
| `PERMISSION_DENIED` | "Location access was denied. Please enable location permissions in your browser settings." |
| `POSITION_UNAVAILABLE` | "Unable to determine your location. Please try again or search manually." |
| `TIMEOUT` | "Location request timed out. Please check your connection and try again." |
| `NOT_SUPPORTED` | "Geolocation is not supported by your browser." |
| `INSECURE_CONTEXT` | "Location requires a secure (HTTPS) connection." |

### Backend Coordinate Errors

| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| Invalid lat range | 422 | "Latitude must be between -90 and 90" |
| Invalid lon range | 422 | "Longitude must be between -180 and 180" |
| Missing paired coord | 422 | "Both latitude and longitude are required" |
| No results for coords | 404 | "No weather data found for this location" |

## Security Considerations

1. **No Location Logging**: Coordinates are NOT logged in application logs
2. **HTTPS Required**: Geolocation API requires secure context
3. **User-Initiated Only**: Never auto-detect location without user action
4. **No Storage**: Coordinates are not persisted anywhere

## Testing Strategy

### Unit Tests
- Weather service with coordinates
- Input validation for lat/lon
- Error handling for invalid coordinates

### Integration Tests
- Full flow with mocked OpenWeatherMap API
- Coordinate to weather response

### Manual Testing
- Test on mobile device
- Test permission denied flow
- Test with VPN (location mismatch)
- Test on HTTP vs HTTPS
