# ============================================
# Weather App - Azure OIDC Setup Script (PowerShell)
# ============================================
# This script creates the minimal Azure resources needed for
# GitHub Actions to authenticate via OIDC and deploy resources.
#
# Prerequisites:
#   - Azure CLI installed and logged in
#   - GitHub CLI installed and authenticated
#
# Usage:
#   .\setup-azure-oidc.ps1 [-GitHubRepo "owner/repo"] [-Location "uksouth"]
#
# Example:
#   .\setup-azure-oidc.ps1 -GitHubRepo "owainow/end-to-end-ai-sdlc" -Location "uksouth"
# ============================================

param(
    [string]$GitHubRepo = "owainow/end-to-end-ai-sdlc",
    [string]$Location = "uksouth"
)

$ErrorActionPreference = "Stop"
$AppName = "GitHub-Actions-WeatherApp"

Write-Host "🔧 Setting up Azure OIDC for: $GitHubRepo" -ForegroundColor Cyan
Write-Host "   Location: $Location"
Write-Host ""

# Get current subscription info
$SubscriptionId = az account show --query id -o tsv
$TenantId = az account show --query tenantId -o tsv
Write-Host "📋 Subscription: $SubscriptionId" -ForegroundColor Gray
Write-Host "📋 Tenant: $TenantId" -ForegroundColor Gray
Write-Host ""

# ============================================
# Step 1: Create App Registration
# ============================================
Write-Host "1️⃣ Creating App Registration..." -ForegroundColor Yellow
$AppId = az ad app create --display-name $AppName --query appId -o tsv
$ObjectId = az ad app show --id $AppId --query id -o tsv
Write-Host "   App ID: $AppId" -ForegroundColor Green

# ============================================
# Step 2: Create Service Principal
# ============================================
Write-Host "2️⃣ Creating Service Principal..." -ForegroundColor Yellow
az ad sp create --id $AppId 2>$null | Out-Null
Write-Host "   Service Principal created" -ForegroundColor Green

# ============================================
# Step 3: Add Federated Credential for main branch
# ============================================
Write-Host "3️⃣ Adding Federated Credential for main branch..." -ForegroundColor Yellow

$FedCredJson = @"
{
    "name": "github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:${GitHubRepo}:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
}
"@

$TempFile = Join-Path $env:TEMP "fed-cred.json"
$FedCredJson | Out-File -FilePath $TempFile -Encoding utf8

az ad app federated-credential create --id $ObjectId --parameters "@$TempFile" 2>$null | Out-Null
Write-Host "   Federated credential added" -ForegroundColor Green

# ============================================
# Step 4: Grant Contributor Role on Subscription
# ============================================
Write-Host "4️⃣ Granting Contributor role on subscription..." -ForegroundColor Yellow
az role assignment create `
    --assignee $AppId `
    --role Contributor `
    --scope "/subscriptions/$SubscriptionId" 2>$null | Out-Null
Write-Host "   Contributor role assigned" -ForegroundColor Green

# ============================================
# Step 5: Configure GitHub Repository Variables
# ============================================
Write-Host "5️⃣ Configuring GitHub repository variables..." -ForegroundColor Yellow
gh variable set AZURE_CLIENT_ID --body $AppId --repo $GitHubRepo
gh variable set AZURE_TENANT_ID --body $TenantId --repo $GitHubRepo
gh variable set AZURE_SUBSCRIPTION_ID --body $SubscriptionId --repo $GitHubRepo
Write-Host "   GitHub variables configured" -ForegroundColor Green

# ============================================
# Summary
# ============================================
Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Values configured in GitHub ($GitHubRepo):" -ForegroundColor Cyan
Write-Host "   AZURE_CLIENT_ID: $AppId"
Write-Host "   AZURE_TENANT_ID: $TenantId"
Write-Host "   AZURE_SUBSCRIPTION_ID: $SubscriptionId"
Write-Host ""
Write-Host "⚠️  Don't forget to set the OPENWEATHERMAP_API_KEY secret:" -ForegroundColor Yellow
Write-Host "   gh secret set OPENWEATHERMAP_API_KEY --body `"your-api-key`" --repo $GitHubRepo"
Write-Host ""
Write-Host "🚀 Push your code to main to trigger the deployment!" -ForegroundColor Cyan
