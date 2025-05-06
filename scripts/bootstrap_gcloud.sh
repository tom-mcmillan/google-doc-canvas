#!/usr/bin/env bash
set -euo pipefail

# Ensure gcloud CLI is installed
if ! command -v gcloud > /dev/null 2>&1; then
  echo "Error: gcloud CLI not found. Please install the Google Cloud SDK:" >&2
  echo "  https://cloud.google.com/sdk/docs/install" >&2
  echo "After installing, run 'gcloud init' to authorize and set up your account." >&2
  exit 1
fi

# Bootstrap Google Cloud infra for Google Docs & Drive Activity sync

# Prompt for GCP project ID if not set
if [ -z "${PROJECT_ID:-}" ]; then
  read -p "Enter your GCP project ID: " PROJECT_ID
fi

# Configure gcloud to use the project
echo "Setting gcloud project to $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling Google Docs and Drive Activity APIs..."
gcloud services enable docs.googleapis.com driveactivity.googleapis.com

# Service account details
SA_NAME="doc-syncer"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account if it doesn't exist
existing_sa=$(gcloud iam service-accounts list \
  --project="$PROJECT_ID" \
  --filter="email=${SA_EMAIL}" \
  --format="value(email)" || true)
if [ -z "$existing_sa" ]; then
  echo "Creating service account $SA_NAME..."
  gcloud iam service-accounts create "$SA_NAME" \
    --project="$PROJECT_ID" \
    --display-name="Doc Syncer Service Account"
else
  echo "Service account $SA_NAME already exists."
fi

# Create a new key for the service account
KEY_FILE="credentials.json"
echo "Generating new key file at $KEY_FILE (will overwrite if exists)..."
gcloud iam service-accounts keys create "$KEY_FILE" \
  --project="$PROJECT_ID" \
  --iam-account="$SA_EMAIL"

echo "Bootstrap complete!"
echo "Next steps:"
echo " 1) Share your target Google Doc with the service account email:  "
echo "    $SA_EMAIL  (Viewer permission)"
echo " 2) Export the credentials file path:"
echo "    export GOOGLE_APPLICATION_CREDENTIALS=\"$(pwd)/$KEY_FILE\""
echo " 3) Run the sync and activity scripts per README.md"