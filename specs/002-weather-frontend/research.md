# Research: Weather Frontend

> **Spec:** 002-weather-frontend  
> **Created:** 2026-01-20

---

## 1. Technology Decisions

### 1.1 Vanilla JavaScript (Selected)

**Why Vanilla JS over frameworks:**
- Zero build step required - just serve static files
- No node_modules or bundler complexity
- Faster initial load (no framework overhead)
- Easier to understand and maintain for small apps
- Modern JS (ES6+) provides sufficient capabilities

**Modern JS features to leverage:**
- `fetch()` for HTTP requests
- `async/await` for clean async code
- Template literals for HTML generation
- `localStorage` API for persistence
- ES6 modules (optional, can use single file)

**Trade-offs:**
- Manual DOM manipulation (no virtual DOM)
- No reactive state management
- More boilerplate for event handling

---

## 2. CSS Framework: Tailwind CSS

### 2.1 CDN Integration
```html
<script src="https://cdn.tailwindcss.com"></script>
```

**Advantages:**
- No build step required
- Full utility class library available
- Responsive prefixes (sm:, md:, lg:, xl:)
- Dark mode support (if needed later)

**CDN Limitations:**
- Slightly larger initial load (~300KB)
- No purging unused styles
- For production, consider Tailwind CLI build

### 2.2 Key Utility Classes for Weather App
| Purpose | Classes |
|---------|---------|
| Card container | `bg-white rounded-xl shadow-lg p-6` |
| Responsive padding | `p-4 md:p-6 lg:p-8` |
| Flexbox centering | `flex items-center justify-center` |
| Grid layout | `grid grid-cols-2 gap-4` |
| Temperature text | `text-6xl font-bold text-gray-800` |
| Input styling | `w-full px-4 py-2 border rounded-lg focus:ring-2` |
| Button styling | `bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg` |

---

## 3. Icon Libraries

### 3.1 Weather Icons (erikflowers/weather-icons)
**CDN:**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/weather-icons/2.0.12/css/weather-icons.min.css">
```

**Usage:**
```html
<i class="wi wi-day-sunny"></i>
<i class="wi wi-cloudy"></i>
<i class="wi wi-rain"></i>
```

**OpenWeatherMap Icon Code Mapping:**
| OWM Code | Condition | Weather Icon Class |
|----------|-----------|-------------------|
| 01d | Clear (day) | `wi-day-sunny` |
| 01n | Clear (night) | `wi-night-clear` |
| 02d | Few clouds (day) | `wi-day-cloudy` |
| 02n | Few clouds (night) | `wi-night-alt-cloudy` |
| 03d/03n | Scattered clouds | `wi-cloud` |
| 04d/04n | Broken clouds | `wi-cloudy` |
| 09d/09n | Shower rain | `wi-showers` |
| 10d | Rain (day) | `wi-day-rain` |
| 10n | Rain (night) | `wi-night-alt-rain` |
| 11d/11n | Thunderstorm | `wi-thunderstorm` |
| 13d/13n | Snow | `wi-snow` |
| 50d/50n | Mist | `wi-fog` |

### 3.2 Heroicons (for UI elements)
**CDN (via SVG copy-paste or unpkg):**
```html
<!-- Search icon -->
<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
  <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
</svg>
```

**Icons needed:**
- Search (magnifying glass)
- Humidity (droplet)
- Wind (wind lines)
- Thermometer (for feels like)
- Location pin (optional)

---

## 4. API Integration

### 4.1 Existing Weather API Endpoint
```
GET /api/v1/weather?city={city}&units={metric|imperial}
```

**Response Structure:**
```json
{
  "city": "London",
  "country": "GB",
  "temperature": 22.5,
  "feels_like": 24.1,
  "humidity": 65,
  "wind_speed": 5.2,
  "description": "clear sky",
  "icon_code": "01d",
  "units": "metric"
}
```

### 4.2 Fetch Implementation
```javascript
async function fetchWeather(city, units = 'metric') {
  const response = await fetch(`/api/v1/weather?city=${encodeURIComponent(city)}&units=${units}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch weather');
  }
  
  return response.json();
}
```

### 4.3 Error Response Handling
| Status | Meaning | User Message |
|--------|---------|--------------|
| 404 | City not found | "City not found. Please check spelling." |
| 429 | Rate limited | "Too many requests. Please wait." |
| 502 | Provider error | "Weather service unavailable." |
| 500 | Server error | "Something went wrong. Try again." |

---

## 5. State Management

### 5.1 Application State
```javascript
const state = {
  city: '',           // Current search query
  weather: null,      // Weather data from API
  units: 'metric',    // 'metric' or 'imperial'
  loading: false,     // Loading indicator
  error: null         // Error message
};
```

### 5.2 localStorage Persistence
```javascript
// Save preference
localStorage.setItem('weatherUnits', 'imperial');

// Load preference (with default)
const units = localStorage.getItem('weatherUnits') || 'metric';
```

---

## 6. Responsive Design Strategy

### 6.1 Breakpoints (Tailwind defaults)
| Breakpoint | Min Width | Use Case |
|------------|-----------|----------|
| (default) | 0px | Mobile phones |
| sm | 640px | Large phones |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |

### 6.2 Layout Adaptations
| Component | Mobile | Desktop |
|-----------|--------|---------|
| Container | Full width, p-4 | max-w-md centered, p-8 |
| Search input | Full width | Full width |
| Weather card | Full width | Full width in container |
| Stats grid | 2 columns | 2 columns |
| Temperature | text-5xl | text-6xl |

---

## 7. Accessibility Considerations

### 7.1 WCAG 2.1 AA Requirements
- **Color contrast:** Minimum 4.5:1 for normal text
- **Focus indicators:** Visible focus rings on interactive elements
- **Labels:** All inputs have associated labels
- **Alt text:** Icons have aria-labels
- **Keyboard navigation:** All controls keyboard accessible

### 7.2 Implementation
```html
<!-- Accessible search input -->
<label for="city-search" class="sr-only">Enter city name</label>
<input 
  id="city-search" 
  type="text" 
  placeholder="Enter city name..."
  aria-describedby="search-hint"
>
<span id="search-hint" class="sr-only">Press Enter to search</span>

<!-- Accessible icon -->
<i class="wi wi-day-sunny" aria-label="Sunny weather"></i>
```

---

## 8. Performance Optimizations

### 8.1 Loading Strategy
1. Inline critical CSS (Tailwind via CDN handles this)
2. Defer non-critical JavaScript (not needed for small app)
3. Use system fonts for fastest text rendering
4. Lazy load weather icons (CSS is small enough to load upfront)

### 8.2 Caching
- API responses cached by backend (15 min TTL)
- Static files can be cached by browser (add cache headers in FastAPI)
- localStorage for unit preference (instant load)

---

## 9. File Structure Decision

**Selected: Single-file approach for simplicity**
```
static/
├── index.html      # Contains HTML + inline CSS customizations + JS
```

**Alternative (if grows):**
```
static/
├── index.html
├── css/
│   └── custom.css
└── js/
    └── app.js
```

For this MVP, a single `index.html` file keeps everything simple and eliminates CORS/module loading complexity.

---

## 10. References

- [Tailwind CSS CDN](https://tailwindcss.com/docs/installation/play-cdn)
- [Weather Icons](https://erikflowers.github.io/weather-icons/)
- [Heroicons](https://heroicons.com/)
- [OpenWeatherMap Icon Codes](https://openweathermap.org/weather-conditions)
- [MDN Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
