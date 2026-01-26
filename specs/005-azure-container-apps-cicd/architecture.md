# Architecture: Azure Container Apps CI/CD Pipeline

## Overview
This document describes the architecture for the CI/CD pipeline that builds and deploys the Weather App to Azure Container Apps using GitHub Actions.

## Architecture Decisions

### AD-001: OIDC Authentication (Federated Credentials)
**Decision**: Use OpenID Connect (OIDC) for GitHub to Azure authentication

**Context**: 
- Need secure authentication from GitHub Actions to Azure
- Don't want to manage long-lived service principal secrets

**Options Considered**:
1. **Service Principal with Secret** 
   - Pros: Simple setup
   - Cons: Secret rotation required, security risk if leaked

2. **OIDC Federated Credentials** (Selected)
   - Pros: No secrets to manage, short-lived tokens, Azure best practice
   - Cons: Slightly more complex initial setup

**Rationale**: OIDC is the recommended approach by both GitHub and Microsoft for secure CI/CD.

### AD-002: Azure Container Apps vs Other Hosting
**Decision**: Use Azure Container Apps for hosting

**Context**: 
- Need serverless container hosting with auto-scaling
- Want managed ingress with HTTPS

**Options Considered**:
1. **Azure App Service**
   - Pros: Simple, well-established
   - Cons: Less container-native, more expensive at scale

2. **Azure Kubernetes Service (AKS)**
   - Pros: Full Kubernetes power
   - Cons: Overkill for single app, operational overhead

3. **Azure Container Apps** (Selected)
   - Pros: Serverless containers, built-in ingress, scale-to-zero, Dapr support
   - Cons: Newer service, fewer features than AKS

**Rationale**: Container Apps is the right balance of simplicity and container-native features for this application.

### AD-003: Single Dockerfile with Multi-Stage Build
**Decision**: Use multi-stage Dockerfile for optimized production image

**Context**: 
- Need small, secure production image
- Want fast builds with dependency caching

**Rationale**: Multi-stage builds separate build dependencies from runtime, resulting in smaller, more secure images.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              GitHub Repository                                   │
│  ┌─────────────┐    ┌─────────────────────────────────────────────────────────┐ │
│  │   PR Merge  │───▶│              GitHub Actions Workflow                    │ │
│  │   to main   │    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐  │ │
│  └─────────────┘    │  │ Checkout│─▶│  Build  │─▶│  Push   │─▶│  Deploy   │  │ │
│                     │  │   Code  │  │  Docker │  │  to ACR │  │  to ACA   │  │ │
│                     │  └─────────┘  └─────────┘  └─────────┘  └───────────┘  │ │
│                     └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ OIDC Token
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    Azure                                         │
│  ┌──────────────────────┐    ┌──────────────────────────────────────────────┐   │
│  │  Entra ID            │    │  Resource Group                              │   │
│  │  ┌────────────────┐  │    │  ┌─────────────────┐  ┌───────────────────┐  │   │
│  │  │ App Registration│  │    │  │ Container       │  │ Container Apps    │  │   │
│  │  │ + Federated     │  │    │  │ Registry (ACR)  │  │ Environment       │  │   │
│  │  │   Credential    │  │    │  │                 │  │ ┌───────────────┐ │  │   │
│  │  └────────────────┘  │    │  │  weatherapp:    │  │ │ weatherapp    │ │  │   │
│  └──────────────────────┘    │  │  - latest       │─▶│ │ Container App │ │  │   │
│                              │  │  - abc123       │  │ │               │ │  │   │
│                              │  └─────────────────┘  │ └───────────────┘ │  │   │
│                              │                       └───────────────────────┘   │
│                              └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ HTTPS
                                         ▼
                              ┌─────────────────────┐
                              │      Internet       │
                              │   weatherapp.xyz    │
                              └─────────────────────┘
```

## Workflow Stages

### Stage 1: Build
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Set up Docker Buildx
      - Login to Azure (OIDC)
      - Login to ACR
      - Build and push Docker image
```

### Stage 2: Deploy
```yaml
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - Login to Azure (OIDC)
      - Deploy to Container Apps
      - Verify health check
```

## File Structure

```
weatherapp/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Main deployment workflow
├── Dockerfile                   # Multi-stage build
├── .dockerignore               # Exclude unnecessary files
└── ... (existing files)
```

## Dockerfile Design

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY src/ ./src/
COPY static/ ./static/
EXPOSE 8000
USER nobody
CMD ["uvicorn", "src.main:get_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

## GitHub Secrets & Variables Required

### Secrets (sensitive)
| Name | Description |
|------|-------------|
| `OPENWEATHERMAP_API_KEY` | API key for weather data |

### Variables (non-sensitive)
| Name | Description | Example |
|------|-------------|---------|
| `AZURE_CLIENT_ID` | App registration client ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_TENANT_ID` | Azure AD tenant ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `ACR_NAME` | Container registry name | `weatherappacr` |
| `ACA_NAME` | Container app name | `weatherapp` |
| `ACA_RESOURCE_GROUP` | Resource group name | `weatherapp-rg` |

## Azure Resource Configuration

### Container App Settings
```yaml
configuration:
  ingress:
    external: true
    targetPort: 8000
    transport: http
  secrets:
    - name: openweathermap-api-key
      value: <from-github-secret>
template:
  containers:
    - name: weatherapp
      image: <acr>.azurecr.io/weatherapp:latest
      resources:
        cpu: 0.5
        memory: 1Gi
      env:
        - name: OPENWEATHERMAP_API_KEY
          secretRef: openweathermap-api-key
        - name: ENVIRONMENT
          value: production
      probes:
        - type: readiness
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        - type: liveness
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
  scale:
    minReplicas: 1
    maxReplicas: 3
```

## Security Considerations

1. **OIDC Authentication**: No long-lived secrets in GitHub
2. **Non-root Container**: Run as `nobody` user
3. **Secret Injection**: API keys from GitHub Secrets → Azure Container Apps secrets
4. **HTTPS Only**: Container Apps provides managed TLS
5. **Minimal Image**: Only runtime dependencies included

## Testing Strategy

1. **Local Docker Build**: Test Dockerfile builds correctly
2. **Dry Run**: Workflow with `--dry-run` flag for deploy command
3. **Health Checks**: Verify `/health` endpoint responds after deploy
4. **Smoke Test**: Verify weather API returns data post-deployment
