# Feature 005: Azure Container Apps CI/CD Pipeline

## Overview
Implement a GitHub Actions workflow that automatically builds and deploys the Weather App to Azure Container Apps when a pull request is merged to the main branch. This enables continuous deployment with zero-downtime updates.

## Problem Statement
Currently, the Weather App has no automated deployment pipeline. Developers must manually build and deploy the application, which is:
- Error-prone and inconsistent
- Time-consuming
- Not scalable for a team environment
- Lacks visibility into deployment status

## Proposed Solution
Create a GitHub Actions workflow that:
1. Triggers on PR merge to main branch
2. Builds a Docker container image
3. Pushes the image to Azure Container Registry (ACR)
4. Deploys to Azure Container Apps with zero-downtime rolling update

## User Stories

### US-001: Automated Deployment
**As a** developer  
**I want** my code to be automatically deployed when my PR is merged  
**So that** I don't have to perform manual deployment steps

### US-002: Deployment Visibility
**As a** team lead  
**I want** to see deployment status in GitHub  
**So that** I can track when changes go live

### US-003: Rollback Capability
**As an** operator  
**I want** to be able to rollback to a previous version  
**So that** I can recover quickly from bad deployments

## Functional Requirements

### FR-001: GitHub Actions Workflow Trigger
- **Priority**: Must
- **Description**: Workflow triggers on push to main branch (after PR merge)
- **Acceptance Criteria**:
  - Workflow runs automatically when PR is merged
  - Workflow can also be triggered manually (workflow_dispatch)
  - Workflow skips if only documentation files changed

### FR-002: Docker Build
- **Priority**: Must
- **Description**: Build optimized Docker image for the FastAPI application
- **Acceptance Criteria**:
  - Multi-stage Dockerfile for minimal image size
  - Image tagged with git SHA and "latest"
  - Build caches dependencies for faster builds
  - Health check endpoint configured

### FR-003: Azure Container Registry Push
- **Priority**: Must
- **Description**: Push built image to Azure Container Registry
- **Acceptance Criteria**:
  - Authenticate using OIDC (federated credentials, no secrets)
  - Push both SHA-tagged and latest-tagged images
  - Registry name configurable via repository variables

### FR-004: Azure Container Apps Deployment
- **Priority**: Must
- **Description**: Deploy container to Azure Container Apps
- **Acceptance Criteria**:
  - Zero-downtime rolling deployment
  - Environment variables configured from GitHub secrets
  - Ingress enabled with HTTPS
  - Health probes configured for readiness/liveness

### FR-005: Deployment Status Reporting
- **Priority**: Should
- **Description**: Report deployment status back to GitHub
- **Acceptance Criteria**:
  - GitHub deployment environment shows status
  - Link to live application in deployment summary
  - Failure notifications visible in PR/commit

## Non-Functional Requirements

### NFR-001: Security
- Use OIDC for Azure authentication (no long-lived secrets)
- API keys stored in GitHub secrets, injected at runtime
- Container runs as non-root user

### NFR-002: Performance
- Build time under 5 minutes
- Deployment time under 3 minutes
- Image size under 200MB

### NFR-003: Reliability
- Automatic retry on transient failures
- Rollback if health checks fail post-deployment

## Out of Scope
- Multi-environment deployments (staging/prod) - future enhancement
- Database migrations - no database currently
- Blue/green deployments - rolling update sufficient for now
- Infrastructure as Code (Bicep/Terraform) for initial Azure resources

## Azure Resources Required
1. **Azure Container Registry** - to store Docker images
2. **Azure Container Apps Environment** - hosting environment
3. **Azure Container App** - the application instance
4. **Managed Identity** - for GitHub OIDC authentication

## Success Metrics
- 100% of merged PRs trigger successful deployments
- Mean deployment time < 5 minutes
- Zero manual intervention required for standard deployments
