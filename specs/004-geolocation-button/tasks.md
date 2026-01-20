# Tasks: Geolocation Button

## Phase 1: Backend - Coordinate-Based Weather Lookup

### T001: Extend Weather Client for Coordinates
- **Priority**: Must
- **Estimate**: 30 min
- **File**: `src/infrastructure/weather_client.py`
- **Description**: Add method to fetch weather by latitude/longitude

**Acceptance Criteria**:
- [ ] Add `get_weather_by_coords(lat: float, lon: float, units: str)` method
- [ ] Call OpenWeatherMap API with `lat` and `lon` parameters
- [ ] Return same `WeatherData` structure as city-based lookup
- [ ] Include city name from API response (reverse geocoded by OpenWeatherMap)

**Implementation Notes**:
```python
# OpenWeatherMap endpoint for coordinates:
# https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units={units}
```

---

### T002: Extend Weather Service for Coordinates
- **Priority**: Must
- **Estimate**: 20 min
- **File**: `src/application/weather_service.py`
- **Description**: Add service method that handles coordinate-based weather requests

**Acceptance Criteria**:
- [ ] Add `get_weather_by_coordinates(lat: float, lon: float, units: str)` method
- [ ] Use caching with coordinates as cache key (round to 2 decimal places for cache efficiency)
- [ ] Return `WeatherResponse` with city name from reverse lookup

**Implementation Notes**:
- Cache key format: `weather:coords:{lat:.2f}:{lon:.2f}:{units}`
- Round coordinates to 2 decimal places (~1km precision) for cache hits

---

### T003: Extend Weather Router for Coordinates
- **Priority**: Must
- **Estimate**: 30 min
- **File**: `src/presentation/routers/weather.py`
- **Description**: Add optional `lat` and `lon` query parameters to weather endpoint

**Acceptance Criteria**:
- [ ] Add optional `lat: float = None` and `lon: float = None` query params
- [ ] Validate: if one coord provided, both must be provided
- [ ] Validate: lat in range [-90, 90], lon in range [-180, 180]
- [ ] If coords provided, use coordinate-based lookup (ignore city param)
- [ ] If no coords, require city param (existing behavior)
- [ ] Return 422 with clear error message for validation failures

**Implementation Notes**:
```python
@router.get("/weather")
async def get_weather(
    city: str | None = None,
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
    units: str = "metric"
):
    # Validation logic...
```

---

### T004: Unit Tests for Coordinate Weather
- **Priority**: Must
- **Estimate**: 30 min
- **Files**: `tests/unit/test_weather_service.py`, `tests/unit/test_weather_router.py`
- **Description**: Add unit tests for coordinate-based weather functionality

**Acceptance Criteria**:
- [ ] Test weather service `get_weather_by_coordinates()` success case
- [ ] Test router with valid lat/lon returns weather
- [ ] Test router with lat only (no lon) returns 422
- [ ] Test router with lon only (no lat) returns 422
- [ ] Test router with out-of-range lat returns 422
- [ ] Test router with out-of-range lon returns 422
- [ ] Test router prefers coords over city when both provided
- [ ] Test router requires city when no coords provided

---

## Phase 2: Frontend - Geolocation Button UI

### T005: Add Geolocation Button HTML
- **Priority**: Must
- **Estimate**: 20 min
- **File**: `static/index.html`
- **Description**: Add the location button to the search section

**Acceptance Criteria**:
- [ ] Add button between city input and search button
- [ ] Use location/crosshair icon (SVG)
- [ ] Button has `id="location-btn"`
- [ ] Include `aria-label="Use my location"`
- [ ] Style consistent with existing buttons (Tailwind)
- [ ] Minimum 44x44px touch target

**Implementation Notes**:
```html
<button 
    id="location-btn" 
    type="button"
    class="px-3 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors..."
    aria-label="Use my location"
>
    <!-- Location pin SVG icon -->
</button>
```

---

### T006: Add Geolocation Button Loading State
- **Priority**: Must
- **Estimate**: 15 min
- **File**: `static/index.html`
- **Description**: Add loading spinner state for location button

**Acceptance Criteria**:
- [ ] Add hidden spinner element inside location button
- [ ] Add `id="location-btn-icon"` and `id="location-btn-spinner"`
- [ ] When geolocating: hide icon, show spinner, disable button
- [ ] Add element to `elements` object in JavaScript

---

### T007: Implement Geolocation JavaScript Handler
- **Priority**: Must
- **Estimate**: 45 min
- **File**: `static/index.html`
- **Description**: Implement the geolocation detection and API call logic

**Acceptance Criteria**:
- [ ] Add `handleGeolocation()` async function
- [ ] Check `navigator.geolocation` support
- [ ] Call `getCurrentPosition()` with 10 second timeout
- [ ] On success: call weather API with lat/lon
- [ ] On error: show appropriate error message
- [ ] Update state: `geolocating: true/false`
- [ ] Disable search controls while geolocating

**Implementation Notes**:
```javascript
async function handleGeolocation() {
    if (!navigator.geolocation) {
        showError('Geolocation is not supported by your browser.');
        return;
    }
    
    state.geolocating = true;
    showGeolocationLoading();
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude } = position.coords;
            await fetchWeatherByCoords(latitude, longitude, state.units);
        },
        (error) => {
            handleGeolocationError(error);
        },
        { timeout: 10000, enableHighAccuracy: false }
    );
}
```

---

### T008: Add fetchWeatherByCoords Function
- **Priority**: Must
- **Estimate**: 20 min
- **File**: `static/index.html`
- **Description**: Add function to fetch weather using coordinates

**Acceptance Criteria**:
- [ ] Add `fetchWeatherByCoords(lat, lon, units)` async function
- [ ] Call `/api/v1/weather?lat={lat}&lon={lon}&units={units}`
- [ ] On success: update state, render weather card
- [ ] On error: show error message
- [ ] Update city input with detected city name

**Implementation Notes**:
```javascript
async function fetchWeatherByCoords(lat, lon, units) {
    const url = `/api/v1/weather?lat=${lat}&lon=${lon}&units=${units}`;
    // ... fetch and handle response
    // Update city input: elements.cityInput.value = weather.city;
}
```

---

### T009: Implement Geolocation Error Handling
- **Priority**: Must
- **Estimate**: 20 min
- **File**: `static/index.html`
- **Description**: Handle all geolocation error cases with user-friendly messages

**Acceptance Criteria**:
- [ ] Add `handleGeolocationError(error)` function
- [ ] Handle `error.code === 1` (PERMISSION_DENIED)
- [ ] Handle `error.code === 2` (POSITION_UNAVAILABLE)
- [ ] Handle `error.code === 3` (TIMEOUT)
- [ ] Display error in existing error container
- [ ] Reset loading state on error

**Implementation Notes**:
```javascript
function handleGeolocationError(error) {
    const messages = {
        1: 'Location access was denied. Please enable location in your browser settings.',
        2: 'Unable to determine your location. Please try again or search manually.',
        3: 'Location request timed out. Please try again.'
    };
    showError(messages[error.code] || 'An unknown error occurred.');
}
```

---

### T010: Wire Up Event Listener
- **Priority**: Must
- **Estimate**: 10 min
- **File**: `static/index.html`
- **Description**: Connect the geolocation button to the handler

**Acceptance Criteria**:
- [ ] Add location button to `elements` object
- [ ] Add click event listener in `init()` function
- [ ] Ensure button is keyboard accessible (Enter/Space triggers)

---

## Phase 3: Polish & Testing

### T011: Add Help Page FAQ Entry
- **Priority**: Should
- **Estimate**: 10 min
- **File**: `static/index.html`
- **Description**: Add FAQ entry explaining the geolocation feature

**Acceptance Criteria**:
- [ ] Add FAQ item: "How do I use my current location?"
- [ ] Explain the feature and permission requirements
- [ ] Add to "Getting Started" category

---

### T012: Integration Testing
- **Priority**: Should
- **Estimate**: 30 min
- **File**: `tests/integration/test_weather_api.py`
- **Description**: Add integration tests for coordinate-based weather

**Acceptance Criteria**:
- [ ] Test full flow: coords → weather response
- [ ] Test with mocked OpenWeatherMap API
- [ ] Verify response includes city name

---

### T013: Manual Testing Checklist
- **Priority**: Must
- **Estimate**: 20 min
- **Description**: Manually verify all geolocation scenarios

**Acceptance Criteria**:
- [ ] Test button click → permission prompt appears
- [ ] Test permission granted → weather loads
- [ ] Test permission denied → error message shown
- [ ] Test on mobile device (if available)
- [ ] Test keyboard navigation to button
- [ ] Test screen reader announces button correctly
- [ ] Verify loading state displays correctly
- [ ] Verify detected city appears in search input

---

## Summary

| Phase | Tasks | Total Estimate |
|-------|-------|----------------|
| Phase 1: Backend | T001-T004 | 1h 50min |
| Phase 2: Frontend | T005-T010 | 2h 10min |
| Phase 3: Polish | T011-T013 | 1h |
| **Total** | **13 tasks** | **~5 hours** |

## Dependencies

```
T001 → T002 → T003 → T004
                  ↓
            T005 → T006 → T007 → T008 → T009 → T010
                                                  ↓
                                            T011, T012, T013
```

Phase 1 (backend) must complete before Phase 2 (frontend) can call the API with coordinates.
