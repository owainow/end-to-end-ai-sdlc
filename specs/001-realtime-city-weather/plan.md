# Implementation Plan: Real-Time City Weather

**Branch**: `001-realtime-city-weather` | **Date**: 2026-01-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-realtime-city-weather/spec.md`

## Summary

Build a REST API endpoint that retrieves real-time weather data for a city by name. The API will integrate with an external weather provider (OpenWeatherMap), support metric/imperial units, implement 15-minute caching with fallback behavior, and include structured logging with request metrics. Built with FastAPI following Clean Architecture principles for Azure deployment.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, httpx (async HTTP client), pydantic (validation), python-dotenv  
**Storage**: In-memory cache (TTL-based) for MVP; Redis optional for production scale  
**Testing**: pytest + pytest-asyncio + pytest-cov  
**Target Platform**: Azure App Service / Azure Container Apps (Linux)
**Project Type**: Single API project  
**Performance Goals**: <3s p95 response time, support 100 concurrent requests  
**Constraints**: 15-minute cache staleness threshold, rate limit handling with retry-after  
**Scale/Scope**: Public API, no authentication required for MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. API-First Design** | ✅ PASS | OpenAPI contract will be defined in Phase 1; FastAPI auto-generates docs |
| **II. Clean Architecture** | ✅ PASS | 4-layer structure planned: Domain (entities), Application (use cases), Infrastructure (weather provider adapter, cache), Presentation (FastAPI routes) |
| **Technology Stack** | ✅ PASS | FastAPI, Python 3.11+, pytest, Ruff, mypy - all per constitution |
| **Testing Requirements** | ✅ PASS | Unit + integration tests planned; 80% coverage target |
| **Code Review Requirements** | ✅ PASS | PR workflow with conventional commits |

**Gate Status**: ✅ All gates pass - proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-realtime-city-weather/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── domain/
│   ├── __init__.py
│   ├── entities.py          # WeatherData, Location, WeatherRequest
│   └── exceptions.py        # Domain-specific exceptions
├── application/
│   ├── __init__.py
│   ├── use_cases.py         # GetWeatherUseCase
│   └── interfaces.py        # WeatherProviderPort, CachePort
├── infrastructure/
│   ├── __init__.py
│   ├── weather_provider.py  # OpenWeatherMap adapter
│   ├── cache.py             # TTL cache implementation
│   └── config.py            # Environment configuration
├── presentation/
│   ├── __init__.py
│   ├── api.py               # FastAPI app and routes
│   ├── schemas.py           # Pydantic request/response models
│   └── middleware.py        # Logging, metrics middleware
└── main.py                  # Application entry point

tests/
├── unit/
│   ├── test_entities.py
│   ├── test_use_cases.py
│   └── test_cache.py
├── integration/
│   ├── test_api.py
│   └── test_weather_provider.py
└── conftest.py              # Shared fixtures
```

**Structure Decision**: Single API project following Clean Architecture with 4 distinct layers. Tests mirror source structure with unit/ and integration/ separation per constitution requirements.

## Complexity Tracking

> No constitution violations requiring justification.
