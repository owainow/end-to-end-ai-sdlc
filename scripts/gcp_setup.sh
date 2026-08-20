#!/usr/bin/env bash
# One-time GCP setup for the Cloud Run deploy pipeline. Idempotent.
#
# Run this AS YOURSELF (not the VM service account):
#   gcloud auth login --no-launch-browser   # if not already logged in
#   OWM_API_KEY=<real-key> bash scripts/gcp_setup.sh
#
# OWM_API_KEY is optional — a placeholder is stored if unset (app boots,
# live weather calls fail until you update the secret).
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-esoteric-life-501609-i8}"
REGION="europe-west2"
AR_REPO="weatherapp"
DEPLOY_SA="github-deploy"
DEPLOY_SA_EMAIL="${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME_SA="$(gcloud iam service-accounts list --project "$PROJECT_ID" \
  --filter="email~compute@developer" --format="value(email)")"
GH_REPO="owainow/end-to-end-ai-sdlc"

echo "== APIs =="
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com iamcredentials.googleapis.com --project "$PROJECT_ID"

echo "== Artifact Registry repo =="
gcloud artifacts repositories describe "$AR_REPO" --location "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1 || \
gcloud artifacts repositories create "$AR_REPO" --repository-format=docker \
  --location "$REGION" --project "$PROJECT_ID"

echo "== Deploy service account =="
gcloud iam service-accounts describe "$DEPLOY_SA_EMAIL" --project "$PROJECT_ID" >/dev/null 2>&1 || \
gcloud iam service-accounts create "$DEPLOY_SA" --display-name "GitHub Actions deploy" --project "$PROJECT_ID"

echo "== Roles =="
for ROLE in roles/run.admin roles/artifactregistry.writer; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:$DEPLOY_SA_EMAIL" --role "$ROLE" --condition=None >/dev/null
done
# Deployer must be able to act as the runtime SA
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA" \
  --member "serviceAccount:$DEPLOY_SA_EMAIL" --role roles/iam.serviceAccountUser \
  --project "$PROJECT_ID" >/dev/null

echo "== Secret =="
if ! gcloud secrets describe openweathermap-api-key --project "$PROJECT_ID" >/dev/null 2>&1; then
  printf '%s' "${OWM_API_KEY:-placeholder-set-me}" | \
    gcloud secrets create openweathermap-api-key --data-file=- --project "$PROJECT_ID"
elif [ -n "${OWM_API_KEY:-}" ]; then
  printf '%s' "$OWM_API_KEY" | \
    gcloud secrets versions add openweathermap-api-key --data-file=- --project "$PROJECT_ID"
fi
# Runtime SA reads the secret at boot
gcloud secrets add-iam-policy-binding openweathermap-api-key \
  --member "serviceAccount:$RUNTIME_SA" --role roles/secretmanager.secretAccessor \
  --project "$PROJECT_ID" >/dev/null

echo "== SA key -> GitHub secret, project id -> GitHub variable =="
KEY_FILE="$(mktemp)"
gcloud iam service-accounts keys create "$KEY_FILE" \
  --iam-account "$DEPLOY_SA_EMAIL" --project "$PROJECT_ID"
gh secret set GCP_SA_KEY --repo "$GH_REPO" < "$KEY_FILE"
rm -f "$KEY_FILE"
gh variable set GCP_PROJECT_ID --repo "$GH_REPO" --body "$PROJECT_ID"

echo ""
echo "✅ Done. Merge the cloudrun-migration PR (or push to main) to deploy."
echo "   NOTE: SA key auth is the fast path for today — swap to Workload"
echo "   Identity Federation after the demo (no long-lived keys)."
