<!--
Sync Impact Report
==================
Version change: 0.0.0 → 1.0.0 (Initial constitution creation)
Modified principles: N/A (new document)
Added sections: Core Principles (2), Technology Stack, Development Workflow, Governance
Removed sections: None
Templates requiring updates: ✅ No updates required (initial setup)
Follow-up TODOs: None
-->

# Weather App Constitution

## Core Principles

### I. API-First Design

All features MUST be designed as API endpoints before any UI or client implementation begins.

- API contracts (OpenAPI/Swagger specifications) MUST be defined and reviewed before implementation
- Endpoints MUST follow RESTful conventions with consistent naming, versioning, and error handling
- All API responses MUST use structured JSON format with consistent schema patterns
- Breaking changes MUST increment the API version and maintain backward compatibility for at least one version cycle
- API documentation MUST be auto-generated from code annotations and kept in sync with implementation

### II. Clean Architecture

The codebase MUST follow Clean Architecture principles to ensure separation of concerns and testability.

- **Domain Layer**: Core business logic and entities with zero external dependencies
- **Application Layer**: Use cases and application-specific business rules
- **Infrastructure Layer**: External concerns (database, APIs, Azure services) as adapters
- **Presentation Layer**: FastAPI routes and request/response models

Dependencies MUST flow inward only—outer layers depend on inner layers, never the reverse. Each layer MUST be independently testable through dependency injection.

## Technology Stack

The following technology decisions are binding for this project:

| Component | Technology | Rationale |
|-----------|------------|-----------|
| API Framework | FastAPI | Async support, auto-documentation, type safety |
| Hosting | Azure App Service / Azure Container Apps | Scalability, managed infrastructure |
| Python Version | 3.11+ | Latest stable with performance improvements |
| Testing | pytest + pytest-asyncio | Standard Python testing with async support |
| Linting | Ruff | Fast, comprehensive Python linting |
| Type Checking | mypy (strict mode) | Runtime type safety verification |

All Azure-specific configurations MUST be externalized via environment variables or Azure App Configuration to maintain local development parity.

## Development Workflow

### Code Review Requirements

- All changes MUST be submitted via Pull Request
- PRs MUST have at least one approving review from a team member before merge
- PRs MUST pass all automated checks (tests, linting, type checking) before merge
- Commit messages MUST follow Conventional Commits format (`feat:`, `fix:`, `docs:`, etc.)

### Testing Requirements

- Unit tests MUST achieve minimum 80% code coverage for business logic
- Integration tests MUST cover all API endpoints
- Tests MUST run in CI pipeline before merge is permitted
- New features MUST include corresponding test cases in the same PR

### Quality Gates

1. **Pre-commit**: Linting and formatting checks
2. **CI Pipeline**: Full test suite, type checking, security scanning
3. **Pre-deploy**: Integration tests against staging environment

## Governance

This constitution supersedes all other development practices for the Weather App project.

- **Authority**: Only the project owner and designated team members may amend this constitution
- **Amendment Process**: Proposed changes MUST be documented in a PR with rationale, reviewed by at least two team members, and approved before merge
- **Compliance**: All PRs and code reviews MUST verify adherence to these principles
- **Exceptions**: Any deviation from these principles MUST be documented with justification and approved by the project owner

**Version**: 1.0.0 | **Ratified**: 2026-01-19 | **Last Amended**: 2026-01-19
