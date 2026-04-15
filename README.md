# Weather App API

A real-time weather data API built with FastAPI following Clean Architecture principles.

## Features

- 🌡️ **Real-time weather data** - Get current weather conditions for any city
- 📅 **5-day forecast** - View daily forecast summaries for today + next 4 days
- 🔄 **Unit conversion** - Support for metric (°C) and imperial (°F) units
- ⚡ **Caching** - 15-minute TTL cache to reduce API calls
- 📊 **Structured logging** - JSON-formatted logs with structlog
- 🛡️ **Error handling** - Comprehensive exception handling with proper HTTP status codes
- 📖 **API documentation** - Auto-generated OpenAPI docs at `/docs`

## Quick Start

### Prerequisites

- Python 3.11+
- OpenWeatherMap API key (get one at https://openweathermap.org/api)

### Installation

1. Clone the repository:
```bash
cd weatherapp
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENWEATHERMAP_API_KEY
```

5. Run the server:
```bash
python -m uvicorn src.main:get_app --factory --reload
```

6. Visit http://localhost:8000/docs for the API documentation.

## API Endpoints

### GET /api/v1/weather

Get current weather data for a city.

**Query Parameters:**
- `city` (required): City name (e.g., "London", "New York")
- `units` (optional): Temperature units - "metric" (default) or "imperial"

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/weather?city=London&units=metric"
```

**Example Response:**
```json
{
  "city": "London",
  "country": "GB",
  "coordinates": {
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  "temperature": 15.2,
  "feels_like": 14.8,
  "humidity": 72,
  "wind_speed": 4.5,
  "pressure": 1013,
  "visibility": 10000,
  "description": "scattered clouds",
  "units": "metric",
  "timestamp": "2024-01-19T15:30:00Z"
}
```

### GET /health

Health check endpoint.

**Example Response:**
```json
{
  "status": "healthy",
  "version": "v1",
  "environment": "dev"
}
```

## Project Structure

```
weatherapp/
├── src/
│   ├── domain/           # Domain layer (entities, value objects, exceptions)
│   ├── application/      # Application layer (use cases, interfaces)
│   ├── infrastructure/   # Infrastructure layer (external adapters)
│   └── presentation/     # Presentation layer (FastAPI routers, schemas)
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── pyproject.toml       # Project configuration
├── requirements.txt     # Pinned dependencies
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Code Quality

```bash
# Run linter
ruff check src tests

# Auto-fix linting issues
ruff check src tests --fix

# Run type checker
mypy src
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENWEATHERMAP_API_KEY` | OpenWeatherMap API key | Required |
| `CACHE_TTL_SECONDS` | Cache TTL in seconds | 900 (15 min) |
| `FORECAST_CACHE_TTL_SECONDS` | Forecast cache TTL in seconds | 1800 (30 min) |
| `LOG_LEVEL` | Logging level | INFO |
| `ENVIRONMENT` | Deployment environment | dev |

## Architecture

This project follows **Clean Architecture** principles:

1. **Domain Layer** - Business entities, value objects, and domain exceptions
2. **Application Layer** - Use cases and port interfaces (dependency inversion)
3. **Infrastructure Layer** - External adapters (OpenWeatherMap client, cache, logging)
4. **Presentation Layer** - FastAPI routers, schemas, middleware, and exception handlers

## License

MIT
