# Data Model: Weather Frontend

> **Spec:** 002-weather-frontend  
> **Created:** 2026-01-20

---

## 1. Application State

### 1.1 State Object
```javascript
/**
 * Application state managed in memory
 * @typedef {Object} AppState
 */
const state = {
  /** @type {string} Current city being displayed */
  city: '',
  
  /** @type {WeatherData|null} Weather data from API */
  weather: null,
  
  /** @type {'metric'|'imperial'} Temperature unit preference */
  units: 'metric',
  
  /** @type {boolean} Whether a request is in progress */
  loading: false,
  
  /** @type {string|null} Error message to display */
  error: null
};
```

---

## 2. API Response Models

### 2.1 Weather Data (from API)
```javascript
/**
 * Weather data returned from /api/v1/weather
 * @typedef {Object} WeatherData
 * @property {string} city - City name
 * @property {string} country - Country code (e.g., "GB")
 * @property {number} temperature - Current temperature
 * @property {number} feels_like - "Feels like" temperature
 * @property {number} humidity - Humidity percentage (0-100)
 * @property {number} wind_speed - Wind speed (m/s or mph)
 * @property {string} description - Weather description (e.g., "clear sky")
 * @property {string} icon_code - OpenWeatherMap icon code (e.g., "01d")
 * @property {string} units - Unit system used ("metric" or "imperial")
 */

// Example response
const exampleWeather = {
  city: "London",
  country: "GB",
  temperature: 22.5,
  feels_like: 24.1,
  humidity: 65,
  wind_speed: 5.2,
  description: "clear sky",
  icon_code: "01d",
  units: "metric"
};
```

### 2.2 Error Response
```javascript
/**
 * Error response from API
 * @typedef {Object} ErrorResponse
 * @property {string} error - Error type
 * @property {string} detail - Human-readable error message
 */

// Example error
const exampleError = {
  error: "CityNotFoundError",
  detail: "City 'Londoon' not found. Please check the spelling."
};
```

---

## 3. UI Component Models

### 3.1 Weather Card Display
```javascript
/**
 * Computed display values for the weather card
 * @typedef {Object} WeatherDisplay
 * @property {string} location - "City, Country" formatted string
 * @property {string} temperature - Temperature with unit (e.g., "22°C")
 * @property {string} feelsLike - "Feels like" with unit (e.g., "Feels like 24°C")
 * @property {string} humidity - Humidity with % (e.g., "65%")
 * @property {string} windSpeed - Wind with unit (e.g., "5.2 m/s")
 * @property {string} description - Capitalized description
 * @property {string} iconClass - Weather Icons CSS class
 */

function formatWeatherDisplay(weather) {
  const unitSymbol = weather.units === 'metric' ? '°C' : '°F';
  const windUnit = weather.units === 'metric' ? 'm/s' : 'mph';
  
  return {
    location: `${weather.city}, ${weather.country}`,
    temperature: `${Math.round(weather.temperature)}${unitSymbol}`,
    feelsLike: `Feels like ${Math.round(weather.feels_like)}${unitSymbol}`,
    humidity: `${weather.humidity}%`,
    windSpeed: `${weather.wind_speed} ${windUnit}`,
    description: capitalizeFirst(weather.description),
    iconClass: getWeatherIconClass(weather.icon_code)
  };
}
```

---

## 4. Icon Mapping

### 4.1 Weather Icon Code Map
```javascript
/**
 * Maps OpenWeatherMap icon codes to Weather Icons CSS classes
 * @type {Object.<string, string>}
 */
const WEATHER_ICON_MAP = {
  // Clear
  '01d': 'wi-day-sunny',
  '01n': 'wi-night-clear',
  
  // Few clouds
  '02d': 'wi-day-cloudy',
  '02n': 'wi-night-alt-cloudy',
  
  // Scattered clouds
  '03d': 'wi-cloud',
  '03n': 'wi-cloud',
  
  // Broken clouds
  '04d': 'wi-cloudy',
  '04n': 'wi-cloudy',
  
  // Shower rain
  '09d': 'wi-showers',
  '09n': 'wi-showers',
  
  // Rain
  '10d': 'wi-day-rain',
  '10n': 'wi-night-alt-rain',
  
  // Thunderstorm
  '11d': 'wi-thunderstorm',
  '11n': 'wi-thunderstorm',
  
  // Snow
  '13d': 'wi-snow',
  '13n': 'wi-snow',
  
  // Mist/Fog
  '50d': 'wi-fog',
  '50n': 'wi-fog'
};

/**
 * Get Weather Icons class for an icon code
 * @param {string} iconCode - OpenWeatherMap icon code
 * @returns {string} Weather Icons CSS class
 */
function getWeatherIconClass(iconCode) {
  return WEATHER_ICON_MAP[iconCode] || 'wi-na';
}
```

---

## 5. localStorage Schema

### 5.1 Persisted Keys
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `weatherUnits` | `'metric'|'imperial'` | `'metric'` | User's unit preference |
| `lastCity` | `string` | `''` | Last searched city (optional enhancement) |

### 5.2 Storage Functions
```javascript
const STORAGE_KEYS = {
  UNITS: 'weatherUnits',
  LAST_CITY: 'lastCity'
};

/**
 * Get stored unit preference
 * @returns {'metric'|'imperial'}
 */
function getStoredUnits() {
  return localStorage.getItem(STORAGE_KEYS.UNITS) || 'metric';
}

/**
 * Save unit preference
 * @param {'metric'|'imperial'} units
 */
function saveUnits(units) {
  localStorage.setItem(STORAGE_KEYS.UNITS, units);
}
```

---

## 6. DOM Element References

### 6.1 Element IDs
```javascript
/**
 * DOM element IDs used in the application
 * @type {Object.<string, string>}
 */
const DOM_IDS = {
  // Search
  SEARCH_INPUT: 'city-search',
  SEARCH_BUTTON: 'search-btn',
  
  // Unit toggle
  UNIT_TOGGLE_METRIC: 'unit-metric',
  UNIT_TOGGLE_IMPERIAL: 'unit-imperial',
  
  // Weather display
  WEATHER_CARD: 'weather-card',
  LOADING_SPINNER: 'loading-spinner',
  ERROR_CONTAINER: 'error-container',
  
  // Weather data
  CITY_NAME: 'city-name',
  TEMPERATURE: 'temperature',
  FEELS_LIKE: 'feels-like',
  HUMIDITY: 'humidity',
  WIND_SPEED: 'wind-speed',
  DESCRIPTION: 'description',
  WEATHER_ICON: 'weather-icon'
};
```

---

## 7. Event Types

### 7.1 User Events
| Event | Target | Handler |
|-------|--------|---------|
| `submit` | Search form | `handleSearch()` |
| `click` | Unit toggle buttons | `handleUnitChange()` |
| `keyup` (Enter) | Search input | `handleSearch()` |

### 7.2 Application Events
| Event | Trigger | Action |
|-------|---------|--------|
| Page load | `DOMContentLoaded` | Initialize state, load preferences |
| Search success | API 200 | Update weather display |
| Search error | API error | Show error message |

---

## 8. Validation Rules

### 8.1 City Input
```javascript
/**
 * Validate city input
 * @param {string} city - User input
 * @returns {{valid: boolean, error: string|null}}
 */
function validateCityInput(city) {
  const trimmed = city.trim();
  
  if (!trimmed) {
    return { valid: false, error: 'Please enter a city name' };
  }
  
  if (trimmed.length < 2) {
    return { valid: false, error: 'City name is too short' };
  }
  
  if (trimmed.length > 100) {
    return { valid: false, error: 'City name is too long' };
  }
  
  return { valid: true, error: null };
}
```

---

## 9. Display Formatting

### 9.1 Helper Functions
```javascript
/**
 * Capitalize first letter of each word
 * @param {string} str
 * @returns {string}
 */
function capitalizeFirst(str) {
  return str.replace(/\b\w/g, char => char.toUpperCase());
}

/**
 * Format temperature with unit
 * @param {number} temp
 * @param {'metric'|'imperial'} units
 * @returns {string}
 */
function formatTemperature(temp, units) {
  const symbol = units === 'metric' ? '°C' : '°F';
  return `${Math.round(temp)}${symbol}`;
}

/**
 * Format wind speed with unit
 * @param {number} speed
 * @param {'metric'|'imperial'} units
 * @returns {string}
 */
function formatWindSpeed(speed, units) {
  const unit = units === 'metric' ? 'm/s' : 'mph';
  return `${speed} ${unit}`;
}
```
