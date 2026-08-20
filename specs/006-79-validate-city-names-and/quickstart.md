# Quickstart: City Name Validation Verification

This guide outlines how to verify the city name boundary validation rules and standardized error handling.

## Running Tests

Run the full pytest suite with coverage:

```bash
pytest --cov=src
```

To run only the unit tests for city validation:

```bash
pytest tests/unit/test_city_validation.py
```

To run integration API tests:

```bash
pytest tests/integration/test_api.py
```

## Manual Verification (cURL Examples)

Start the server locally:

```bash
uvicorn src.main:app --reload --port 8000
```

### 1. Valid City Request

```bash
curl -X GET "http://localhost:8000/api/v1/weather?city=London" -i
```
**Expected Response**: `200 OK` with weather payload.

### 2. Empty City Request

```bash
curl -X GET "http://localhost:8000/api/v1/weather?city=" -i
```
**Expected Response**: `422 Unprocessable Entity`
```json
{
  "error": {
    "code": "UNPROCESSABLE_ENTITY",
    "message": "City name cannot be empty",
    "target": "city",
    "details": [],
    "correlationId": "req-..."
  }
}
```

### 3. Purely Numeric City Request

```bash
curl -X GET "http://localhost:8000/api/v1/weather?city=12345" -i
```
**Expected Response**: `422 Unprocessable Entity`
```json
{
  "error": {
    "code": "UNPROCESSABLE_ENTITY",
    "message": "City name must contain letters and cannot consist only of numbers or special characters",
    "target": "city",
    "details": [],
    "correlationId": "req-..."
  }
}
```

### 4. Over-Long City Request (>100 Chars)

```bash
curl -X GET "http://localhost:8000/api/v1/weather?city=$(python3 -c 'print("a"*101)')" -i
```
**Expected Response**: `422 Unprocessable Entity`
```json
{
  "error": {
    "code": "UNPROCESSABLE_ENTITY",
    "message": "City name must not exceed 100 characters",
    "target": "city",
    "details": [],
    "correlationId": "req-..."
  }
}
```

### 5. Custom Correlation ID Propagation

```bash
curl -X GET "http://localhost:8000/api/v1/weather?city=12345" -H "x-correlation-id: req-custom-123" -i
```
**Expected Response**: `422 Unprocessable Entity`, with response header `x-correlation-id: req-custom-123` and `"correlationId": "req-custom-123"` in error payload.

### 6. Valid Coordinate Lookup without City

```bash
curl -X GET "http://localhost:8000/api/v1/weather?lat=51.5074&lon=-0.1278" -i
```
**Expected Response**: `200 OK` with weather data.
