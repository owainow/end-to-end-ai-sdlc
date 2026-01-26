#!/bin/bash
# ============================================
# Weather App - Azure OIDC Setup Script
# ============================================
# This script creates the minimal Azure resources needed for
# GitHub Actions to authenticate via OIDC and deploy resources.
#
# Prerequisites:
#   - Azure CLI installed and logged in
#   - GitHub CLI installed and authenticated
#
# Usage:
#   ./setup-azure-oidc.sh <github-repo> [location]
#
# Example:
#   ./setup-azure-oidc.sh owainow/end-to-end-ai-sdlc uksouth
# ============================================

set -e

# Parameters
GITHUB_REPO="${1:-owainow/end-to-end-ai-sdlc}"
LOCATION="${2:-uksouth}"
APP_NAME="GitHub-Actions-WeatherApp"

echo "🔧 Setting up Azure OIDC for: $GITHUB_REPO"
echo "   Location: $LOCATION"
echo ""

# Get current subscription info
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "📋 Subscription: $SUBSCRIPTION_ID"
echo "📋 Tenant: $TENANT_ID"
echo ""

# ============================================
# Step 1: Create App Registration
# ============================================
echo "1️⃣ Creating App Registration..."
APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
OBJECT_ID=$(az ad app show --id $APP_ID --query id -o tsv)
echo "   App ID: $APP_ID"

# ============================================
# Step 2: Create Service Principal
# ============================================
echo "2️⃣ Creating Service Principal..."
az ad sp create --id $APP_ID --only-show-errors > /dev/null
echo "   Service Principal created"

# ============================================
# Step 3: Add Federated Credential for main branch
# ============================================
echo "3️⃣ Adding Federated Credential for main branch..."
cat > /tmp/fed-cred.json << EOF
{
    "name": "github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:${GITHUB_REPO}:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
}
EOF

az ad app federated-credential create --id $OBJECT_ID --parameters @/tmp/fed-cred.json --only-show-errors > /dev/null
echo "   Federated credential added"

# ============================================
# Step 4: Grant Contributor Role on Subscription
# ============================================
echo "4️⃣ Granting Contributor role on subscription..."
az role assignment create \
    --assignee $APP_ID \
    --role Contributor \
    --scope /subscriptions/$SUBSCRIPTION_ID \
    --only-show-errors > /dev/null
echo "   Contributor role assigned"

# ============================================
# Step 5: Configure GitHub Repository Variables
# ============================================
echo "5️⃣ Configuring GitHub repository variables..."
gh variable set AZURE_CLIENT_ID --body "$APP_ID" --repo "$GITHUB_REPO"
gh variable set AZURE_TENANT_ID --body "$TENANT_ID" --repo "$GITHUB_REPO"
gh variable set AZURE_SUBSCRIPTION_ID --body "$SUBSCRIPTION_ID" --repo "$GITHUB_REPO"
echo "   GitHub variables configured"

# ============================================
# Summary
# ============================================
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Values configured in GitHub ($GITHUB_REPO):"
echo "   AZURE_CLIENT_ID: $APP_ID"
echo "   AZURE_TENANT_ID: $TENANT_ID"
echo "   AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
echo ""
echo "⚠️  Don't forget to set the OPENWEATHERMAP_API_KEY secret:"
echo "   gh secret set OPENWEATHERMAP_API_KEY --body \"your-api-key\" --repo $GITHUB_REPO"
echo ""
echo "🚀 Push your code to main to trigger the deployment!"
