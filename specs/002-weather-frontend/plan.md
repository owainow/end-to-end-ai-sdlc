# Implementation Plan: Weather Frontend

> **Spec:** 002-weather-frontend  
> **Created:** 2026-01-20

---

## 1. Implementation Strategy

### 1.1 Approach
**Single-file MVP** - All HTML, CSS customizations, and JavaScript in one `index.html` file for maximum simplicity. This approach:
- Eliminates module loading complexity
- Requires no build tools
- Makes deployment trivial (one file to serve)
- Can be refactored into separate files later if needed

### 1.2 Implementation Order
```
Phase 1: Infrastructure Setup
    └── Configure FastAPI static file serving
    
Phase 2: HTML Structure
    └── Create semantic HTML layout
    └── Add Tailwind/Weather Icons CDN links
    
Phase 3: Core Features
    └── Search functionality
    └── API integration
    └── Weather card display
    
Phase 4: Unit Toggle
    └── Toggle UI
    └── localStorage persistence
    └── Re-fetch with new units
    
Phase 5: Polish
    └── Error handling UI
    └── Loading states
    └── Responsive refinements
    └── Accessibility audit
```

---

## 2. Architecture Decisions

### 2.1 State Management
```
┌─────────────────────────────────────────┐
│              Application                │
├─────────────────────────────────────────┤
│  State Object (in-memory)               │
│  ├── city: string                       │
│  ├── weather: WeatherData | null        │
│  ├── units: 'metric' | 'imperial'       │
│  ├── loading: boolean                   │
│  └── error: string | null               │
├─────────────────────────────────────────┤
│  localStorage                           │
│  └── weatherUnits: 'metric' | 'imperial'│
└─────────────────────────────────────────┘
```

### 2.2 Component Structure (Logical)
```
┌─────────────────────────────────────────┐
│              App Container              │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │          Header                 │    │
│  │   Title + Unit Toggle           │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │        Search Section           │    │
│  │   Input + Search Button         │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │      Content Area               │    │
│  │   (one of:)                     │    │
│  │   - Welcome message (initial)   │    │
│  │   - Loading spinner             │    │
│  │   - Weather card                │    │
│  │   - Error message               │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 2.3 Data Flow
```
User types city → Click Search/Enter
         ↓
    Validate input
         ↓
    Set loading = true
         ↓
    fetch('/api/v1/weather?city=X&units=Y')
         ↓
    ┌────────────────────┐
    │   Success (200)    │──→ Update weather state → Render card
    └────────────────────┘
    ┌────────────────────┐
    │   Error (4xx/5xx)  │──→ Set error message → Render error
    └────────────────────┘
         ↓
    Set loading = false
```

---

## 3. File Changes

### 3.1 New Files
| File | Purpose |
|------|---------|
| `static/index.html` | Complete frontend application |

### 3.2 Modified Files
| File | Change |
|------|--------|
| `src/main.py` | Add StaticFiles mount for serving frontend |

---

## 4. UI Component Specifications

### 4.1 Search Input
```html
<!-- Tailwind classes -->
<input 
  type="text"
  class="w-full px-4 py-3 text-lg border-2 border-gray-200 
         rounded-lg focus:border-blue-500 focus:ring-2 
         focus:ring-blue-200 focus:outline-none transition-colors"
  placeholder="Enter city name..."
>
```

### 4.2 Unit Toggle
```html
<!-- Toggle button group -->
<div class="inline-flex rounded-lg border border-gray-200">
  <button class="px-4 py-2 rounded-l-lg bg-blue-500 text-white">°C</button>
  <button class="px-4 py-2 rounded-r-lg bg-white text-gray-700">°F</button>
</div>
```

### 4.3 Weather Card
```html
<div class="bg-white rounded-2xl shadow-xl p-8 max-w-md mx-auto">
  <!-- Location -->
  <h2 class="text-2xl font-semibold text-gray-800">London, GB</h2>
  
  <!-- Main weather -->
  <div class="flex items-center justify-center my-6">
    <i class="wi wi-day-sunny text-6xl text-yellow-500"></i>
    <span class="text-7xl font-bold text-gray-800 ml-4">22°C</span>
  </div>
  
  <!-- Feels like -->
  <p class="text-center text-gray-500">Feels like 24°C</p>
  
  <!-- Stats grid -->
  <div class="grid grid-cols-2 gap-4 mt-6">
    <div class="text-center">
      <i class="wi wi-humidity text-blue-400 text-2xl"></i>
      <p class="text-lg font-medium">65%</p>
      <p class="text-sm text-gray-500">Humidity</p>
    </div>
    <div class="text-center">
      <i class="wi wi-strong-wind text-gray-400 text-2xl"></i>
      <p class="text-lg font-medium">5.2 m/s</p>
      <p class="text-sm text-gray-500">Wind</p>
    </div>
  </div>
  
  <!-- Description -->
  <p class="text-center text-xl text-gray-600 mt-6 capitalize">Clear sky</p>
</div>
```

### 4.4 Loading Spinner
```html
<div class="flex justify-center items-center py-12">
  <div class="animate-spin rounded-full h-12 w-12 border-4 
              border-blue-500 border-t-transparent"></div>
</div>
```

### 4.5 Error Card
```html
<div class="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md mx-auto">
  <div class="flex items-center">
    <svg class="h-6 w-6 text-red-500 mr-3"><!-- Error icon --></svg>
    <p class="text-red-700">City not found. Please check the spelling.</p>
  </div>
</div>
```

---

## 5. JavaScript Functions

### 5.1 Core Functions
| Function | Purpose |
|----------|---------|
| `init()` | Initialize app, load preferences, set up event listeners |
| `handleSearch(event)` | Handle form submission, validate, call API |
| `fetchWeather(city, units)` | Make API request, return data or throw |
| `handleUnitChange(units)` | Update preference, re-fetch if weather exists |

### 5.2 Render Functions
| Function | Purpose |
|----------|---------|
| `renderWeatherCard(weather)` | Display weather data in card |
| `renderError(message)` | Display error message |
| `renderLoading()` | Show loading spinner |
| `hideAllContent()` | Clear content area before rendering |

### 5.3 Utility Functions
| Function | Purpose |
|----------|---------|
| `getWeatherIconClass(iconCode)` | Map icon code to CSS class |
| `formatTemperature(temp, units)` | Format temp with unit symbol |
| `formatWindSpeed(speed, units)` | Format wind with unit |
| `capitalizeFirst(str)` | Capitalize first letter of words |
| `getStoredUnits()` | Get units from localStorage |
| `saveUnits(units)` | Save units to localStorage |

---

## 6. API Integration

### 6.1 Request Flow
```javascript
async function fetchWeather(city, units) {
  const url = `/api/v1/weather?city=${encodeURIComponent(city)}&units=${units}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Error: ${response.status}`);
  }
  
  return response.json();
}
```

### 6.2 Error Mapping
| HTTP Status | Error Type | User Message |
|-------------|------------|--------------|
| 404 | City not found | "City not found. Please check the spelling and try again." |
| 429 | Rate limited | "Too many requests. Please wait a moment and try again." |
| 502 | Provider error | "Weather service is temporarily unavailable." |
| 500 | Server error | "Something went wrong. Please try again later." |
| Network error | Fetch failed | "Unable to connect. Please check your internet connection." |

---

## 7. Responsive Breakpoints

### 7.1 Mobile First Approach
```css
/* Base (mobile): 0-639px */
.container { padding: 1rem; }
.temperature { font-size: 3rem; }

/* sm: 640px+ */
@media (min-width: 640px) {
  .container { padding: 1.5rem; }
}

/* md: 768px+ */
@media (min-width: 768px) {
  .container { padding: 2rem; max-width: 32rem; }
  .temperature { font-size: 4rem; }
}
```

### 7.2 Tailwind Responsive Classes Used
```html
<!-- Container -->
<div class="p-4 md:p-8 max-w-md mx-auto">

<!-- Temperature -->
<span class="text-5xl md:text-7xl">

<!-- Stats grid -->
<div class="grid grid-cols-2 gap-3 md:gap-4">
```

---

## 8. Testing Plan

### 8.1 Manual Test Cases
| Test | Steps | Expected |
|------|-------|----------|
| Search valid city | Enter "London", press Enter | Weather card displays |
| Search invalid city | Enter "asdfghjkl", press Enter | Error message displays |
| Empty search | Click search with empty input | Validation message |
| Toggle to °F | Click °F button | Refreshes with imperial units |
| Toggle persistence | Select °F, refresh page | °F still selected |
| Mobile layout | Resize to 320px | All content visible, no overflow |

### 8.2 Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 9. Deployment Integration

### 9.1 FastAPI Static Files
```python
# src/main.py
from fastapi.staticfiles import StaticFiles
from pathlib import Path

def get_app() -> FastAPI:
    app = create_application()
    
    # ... existing setup ...
    
    # Serve static files (must be last, catches all routes)
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    
    return app
```

### 9.2 Route Priority
1. `/api/v1/*` - API routes (registered first)
2. `/health` - Health check
3. `/*` - Static files (catch-all, last)

---

## 10. Success Criteria Checklist

- [ ] Search box displays and accepts input
- [ ] Search triggers API call with city parameter
- [ ] Weather card displays all required fields
- [ ] Unit toggle switches between °C and °F
- [ ] Unit preference persists in localStorage
- [ ] Error messages display for invalid cities
- [ ] Loading spinner shows during fetch
- [ ] Layout works on mobile (320px)
- [ ] Layout works on desktop (1200px)
- [ ] Weather icons display correctly
- [ ] All interactive elements keyboard accessible
