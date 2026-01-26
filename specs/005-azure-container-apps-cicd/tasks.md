# Tasks: Azure Container Apps CI/CD Pipeline

## Phase 1: Azure Infrastructure Setup (Manual/Portal)

### T001: Create Azure Resource Group
- **Priority**: Must
- **Estimate**: 5 min
- **Description**: Create resource group for all Weather App Azure resources

**Acceptance Criteria**:
- [ ] Resource group created: `weatherapp-rg`
- [ ] Located in appropriate region (e.g., `uksouth` or `eastus`)

**Manual Steps**:
```bash
az group create --name weatherapp-rg --location uksouth
```

---

### T002: Create Azure Container Registry
- **Priority**: Must
- **Estimate**: 10 min
- **Description**: Create ACR to store Docker images

**Acceptance Criteria**:
- [ ] ACR created with unique name (e.g., `weatherappacr<unique>`)
- [ ] SKU: Basic (sufficient for demo)
- [ ] Admin user disabled (using managed identity)

**Manual Steps**:
```bash
az acr create \
  --resource-group weatherapp-rg \
  --name weatherappacr \
  --sku Basic
```

---

### T003: Create Container Apps Environment
- **Priority**: Must
- **Estimate**: 10 min
- **Description**: Create the Container Apps hosting environment

**Acceptance Criteria**:
- [ ] Container Apps environment created
- [ ] Consumption plan (serverless)

**Manual Steps**:
```bash
az containerapp env create \
  --resource-group weatherapp-rg \
  --name weatherapp-env \
  --location uksouth
```

---

### T004: Create App Registration for OIDC
- **Priority**: Must
- **Estimate**: 15 min
- **Description**: Create Azure AD app registration with federated credentials for GitHub Actions

**Acceptance Criteria**:
- [ ] App registration created in Entra ID
- [ ] Federated credential configured for `owainow/end-to-end-ai-sdlc` repo
- [ ] Subject: `repo:owainow/end-to-end-ai-sdlc:ref:refs/heads/main`
- [ ] Contributor role assigned to resource group

**Manual Steps**:
```bash
# Create app registration
az ad app create --display-name "GitHub Actions Weather App"

# Add federated credential (via Portal or CLI)
# Grant Contributor role to resource group
az role assignment create \
  --assignee <app-client-id> \
  --role Contributor \
  --scope /subscriptions/<sub-id>/resourceGroups/weatherapp-rg

# Grant AcrPush role to ACR
az role assignment create \
  --assignee <app-client-id> \
  --role AcrPush \
  --scope /subscriptions/<sub-id>/resourceGroups/weatherapp-rg/providers/Microsoft.ContainerRegistry/registries/weatherappacr
```

---

### T005: Configure GitHub Repository Variables & Secrets
- **Priority**: Must
- **Estimate**: 10 min
- **Description**: Add Azure configuration to GitHub repository settings

**Acceptance Criteria**:
- [ ] Secret: `OPENWEATHERMAP_API_KEY` configured
- [ ] Variable: `AZURE_CLIENT_ID` configured
- [ ] Variable: `AZURE_TENANT_ID` configured
- [ ] Variable: `AZURE_SUBSCRIPTION_ID` configured
- [ ] Variable: `ACR_NAME` configured
- [ ] Variable: `ACA_NAME` configured (e.g., `weatherapp`)
- [ ] Variable: `ACA_RESOURCE_GROUP` configured

---

## Phase 2: Docker Configuration

### T006: Create Dockerfile
- **Priority**: Must
- **Estimate**: 30 min
- **File**: `Dockerfile`
- **Description**: Create multi-stage Dockerfile for production build

**Acceptance Criteria**:
- [ ] Multi-stage build (builder + runtime)
- [ ] Based on `python:3.11-slim`
- [ ] Dependencies installed via wheel for faster builds
- [ ] Static files included
- [ ] Non-root user (`nobody`)
- [ ] Exposes port 8000
- [ ] CMD runs uvicorn with factory pattern

**Implementation**:
```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install wheels from builder stage
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY src/ ./src/
COPY static/ ./static/

# Expose port
EXPOSE 8000

# Run as non-root user
USER nobody

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "src.main:get_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

---

### T007: Create .dockerignore
- **Priority**: Must
- **Estimate**: 10 min
- **File**: `.dockerignore`
- **Description**: Exclude unnecessary files from Docker build context

**Acceptance Criteria**:
- [ ] Excludes `.git`, `.venv`, `__pycache__`
- [ ] Excludes test files, specs, docs
- [ ] Excludes IDE config files

**Implementation**:
```
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
.venv
venv/
ENV/

# Testing
.pytest_cache
.coverage
htmlcov/
tests/

# IDE
.vscode
.idea
*.swp
*.swo

# Docs and specs
*.md
specs/
docs/

# Misc
.DS_Store
*.log
```

---

### T008: Test Docker Build Locally
- **Priority**: Must
- **Estimate**: 15 min
- **Description**: Verify Docker image builds and runs correctly

**Acceptance Criteria**:
- [ ] `docker build` completes successfully
- [ ] Container starts and health check passes
- [ ] Weather API responds correctly
- [ ] Image size under 200MB

**Test Commands**:
```bash
# Build
docker build -t weatherapp:local .

# Run
docker run -d -p 8000:8000 \
  -e OPENWEATHERMAP_API_KEY=<key> \
  --name weatherapp-test \
  weatherapp:local

# Test
curl http://localhost:8000/health
curl "http://localhost:8000/api/v1/weather?city=London"

# Check size
docker images weatherapp:local
```

---

## Phase 3: GitHub Actions Workflow

### T009: Create Deployment Workflow
- **Priority**: Must
- **Estimate**: 45 min
- **File**: `.github/workflows/deploy.yml`
- **Description**: Create the main CI/CD workflow

**Acceptance Criteria**:
- [ ] Triggers on push to main branch
- [ ] Triggers on workflow_dispatch (manual)
- [ ] Builds Docker image with Buildx
- [ ] Pushes to ACR with SHA and latest tags
- [ ] Deploys to Container Apps
- [ ] Uses OIDC authentication
- [ ] Has build and deploy jobs

**Implementation**:
```yaml
name: Build and Deploy to Azure Container Apps

on:
  push:
    branches: [main]
    paths-ignore:
      - '**.md'
      - 'specs/**'
      - 'docs/**'
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

env:
  ACR_NAME: ${{ vars.ACR_NAME }}
  IMAGE_NAME: weatherapp

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Azure
        uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

      - name: Login to ACR
        run: az acr login --name ${{ env.ACR_NAME }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Login to Azure
        uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

      - name: Deploy to Container Apps
        uses: azure/container-apps-deploy-action@v2
        with:
          resourceGroup: ${{ vars.ACA_RESOURCE_GROUP }}
          containerAppName: ${{ vars.ACA_NAME }}
          imageToDeploy: ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}

      - name: Verify deployment
        run: |
          # Wait for deployment to complete
          sleep 30
          
          # Get the app URL
          APP_URL=$(az containerapp show \
            --name ${{ vars.ACA_NAME }} \
            --resource-group ${{ vars.ACA_RESOURCE_GROUP }} \
            --query properties.configuration.ingress.fqdn -o tsv)
          
          # Health check
          curl -f "https://${APP_URL}/health" || exit 1
          
          echo "✅ Deployment verified: https://${APP_URL}"
```

---

### T010: Create Initial Container App (First Deploy)
- **Priority**: Must
- **Estimate**: 15 min
- **Description**: Create the initial Container App resource before first workflow run

**Acceptance Criteria**:
- [ ] Container App created in Azure
- [ ] Ingress configured (external, port 8000)
- [ ] Environment variables configured
- [ ] Connected to ACR with managed identity

**Manual Steps**:
```bash
# Create the container app (first time)
az containerapp create \
  --name weatherapp \
  --resource-group weatherapp-rg \
  --environment weatherapp-env \
  --image mcr.microsoft.com/k8se/quickstart:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3

# Configure ACR pull
az containerapp registry set \
  --name weatherapp \
  --resource-group weatherapp-rg \
  --server weatherappacr.azurecr.io \
  --identity system

# Add secrets
az containerapp secret set \
  --name weatherapp \
  --resource-group weatherapp-rg \
  --secrets openweathermap-api-key=<your-api-key>

# Update environment variables
az containerapp update \
  --name weatherapp \
  --resource-group weatherapp-rg \
  --set-env-vars \
    OPENWEATHERMAP_API_KEY=secretref:openweathermap-api-key \
    ENVIRONMENT=production
```

---

## Phase 4: Testing & Verification

### T011: Test Workflow End-to-End
- **Priority**: Must
- **Estimate**: 20 min
- **Description**: Verify the complete CI/CD pipeline works

**Acceptance Criteria**:
- [ ] Create test PR with minor change
- [ ] Merge PR triggers workflow
- [ ] Build job completes successfully
- [ ] Deploy job completes successfully
- [ ] App accessible at Container Apps URL
- [ ] Health endpoint responds
- [ ] Weather API returns data

---

### T012: Document Deployment Process
- **Priority**: Should
- **Estimate**: 15 min
- **File**: `docs/DEPLOYMENT.md`
- **Description**: Document the deployment setup and troubleshooting

**Acceptance Criteria**:
- [ ] Prerequisites listed
- [ ] Azure setup steps documented
- [ ] GitHub secrets/variables documented
- [ ] Manual deployment instructions
- [ ] Troubleshooting guide

---

## Summary

| Phase | Tasks | Total Estimate |
|-------|-------|----------------|
| Phase 1: Azure Setup | T001-T005 | 50 min |
| Phase 2: Docker | T006-T008 | 55 min |
| Phase 3: GitHub Actions | T009-T010 | 1h |
| Phase 4: Testing | T011-T012 | 35 min |
| **Total** | **12 tasks** | **~3.5 hours** |

## Dependencies

```
T001 → T002 → T003 → T004 → T005
              ↓
        T006 → T007 → T008
                      ↓
              T009 → T010 → T011 → T012
```

## Notes

- **Phase 1** tasks are manual Azure Portal/CLI steps (one-time setup)
- **Phase 2-3** tasks create files that will be committed to the repo
- Consider using `az containerapp up` for simpler initial setup if preferred
- The workflow can be enhanced later with staging environments, approval gates, etc.
