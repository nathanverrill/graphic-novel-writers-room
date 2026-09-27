#!/bin/bash
# Deploy Easel (one static page in one container) to Cloud Run.
set -euo pipefail
PROJECT=evoke-prosperity
REGION=us-central1
HERE="$(cd "$(dirname "$0")" && pwd)"

gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com --project $PROJECT

# Fresh projects don't grant the default compute SA build rights; without this
# the source deploy fails with PERMISSION_DENIED.
SA="$(gcloud projects describe $PROJECT --format 'value(projectNumber)')-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$SA" \
  --role=roles/cloudbuild.builds.builder --condition=None >/dev/null

gcloud run deploy easel --quiet --source "$HERE" --project $PROJECT \
  --region $REGION --allow-unauthenticated --memory 256Mi --max-instances 2
