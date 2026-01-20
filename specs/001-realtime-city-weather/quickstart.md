# Quickstart: Real-Time City Weather API

**Feature Branch**: `001-realtime-city-weather`  
**Date**: 2026-01-19

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- OpenWeatherMap API key (free tier: https://openweathermap.org/api)

## Setup

### 1. Clone and Navigate

```bash
git checkout 001-realtime-city-weather
cd weatherapp
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```env
OPENWEATHERMAP_API_KEY=your_api_key_here
CACHE_TTL_SECONDS=900
LOG_LEVEL=INFO
ENVIRONMENT=dev
```

### 5. Run the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### Get Weather for a City

```bash
# Basic request (metric units, Celsius)
curl "http://localhost:8000/api/v1/weather?city=London"

# With imperial units (Fahrenheit)
curl "http://localhost:8000/api/v1/weather?city=London&units=imperial"

# City with country code
curl "http://localhost:8000/api/v1/weather?city=Paris,FR"
```

### Example Response

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
  "timestamp": "2026-01-19T14:30:00Z"
}
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | VALIDATION_ERROR | Empty city name or invalid parameters |
| 404 | CITY_NOT_FOUND | City not found in weather provider |
| 429 | RATE_LIMITED | Too many requests, check Retry-After header |
| 503 | PROVIDER_UNAVAILABLE | Weather service temporarily unavailable |
| 503 | DATA_STALE | Cached data expired and provider unavailable |

## Development

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

### Linting and Type Checking

```bash
# Lint with Ruff
ruff check src/ tests/

# Type check with mypy
mypy src/ --strict
```

### API Documentation

Once running, access the auto-generated API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Project Structure

```
src/
├── domain/           # Core business logic (no dependencies)
├── application/      # Use cases and interfaces
├── infrastructure/   # External adapters (API, cache)
├── presentation/     # FastAPI routes and schemas
└── main.py           # Application entry point

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── conftest.py       # Shared fixtures
```

## Azure Deployment

### Environment Variables (Azure App Service)

Configure these in Azure Portal > App Service > Configuration:

| Name | Value | Description |
|------|-------|-------------|
| OPENWEATHERMAP_API_KEY | (secret) | Weather provider API key |
| CACHE_TTL_SECONDS | 900 | Cache TTL in seconds |
| LOG_LEVEL | INFO | Logging level |
| ENVIRONMENT | production | Environment name |

### Deploy via Azure CLI

```bash
# Login to Azure
az login

# Create resource group (if needed)
az group create --name weatherapp-rg --location eastus

# Create App Service plan
az appservice plan create --name weatherapp-plan --resource-group weatherapp-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group weatherapp-rg --plan weatherapp-plan --name weatherapp --runtime "PYTHON:3.11"

# Deploy code
az webapp up --name weatherapp --resource-group weatherapp-rg
```

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-19T14:30:00Z"
}
```
