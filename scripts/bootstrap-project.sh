#!/usr/bin/env bash
# Org-admin bootstrap: create non-prod GCP project and apply Terraform.
# Run once when the project does not yet exist (week-1 critical path).
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-peq-tools}"
REGION="${REGION:-us-central1}"
BILLING_ACCOUNT="${BILLING_ACCOUNT:?Set BILLING_ACCOUNT env var}"
MEMBER="${MEMBER:?Set MEMBER env var (e.g. user:andrew@example.com)}"

echo "Creating project: $PROJECT_ID"
gcloud projects create "$PROJECT_ID" --name="Peq Tools" 2>/dev/null || echo "Project may already exist"

echo "Linking billing account"
gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"

echo "Setting active project"
gcloud config set project "$PROJECT_ID"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$SCRIPT_DIR/../infra/terraform"
STATE_BUCKET="${PROJECT_ID}-terraform-state"
SECRET_ID="${PROJECT_ID}-app-config"

cd "$TF_DIR"

if [ ! -f terraform.tfvars ]; then
  cp terraform.tfvars.example terraform.tfvars
  sed -i.bak "s|user:andrew@platformeq.com|$MEMBER|" terraform.tfvars
  sed -i.bak '/user:leo@platformeq.com/d' terraform.tfvars
  rm -f terraform.tfvars.bak
fi

if [ ! -f backend.hcl ]; then
  echo "First apply: using local state until the state bucket exists"
  terraform init -backend=false
  terraform apply -auto-approve \
    -var="project_id=$PROJECT_ID" \
    -var="region=$REGION" \
    -var="developers=[\"$MEMBER\"]"

  echo "Migrating state to gs://${STATE_BUCKET}"
  cat > backend.hcl <<EOF
bucket = "${STATE_BUCKET}"
prefix = "terraform/state"
EOF
  terraform init -backend-config=backend.hcl -migrate-state
else
  terraform init -backend-config=backend.hcl
  terraform apply -auto-approve \
    -var="project_id=$PROJECT_ID" \
    -var="region=$REGION" \
    -var="developers=[\"$MEMBER\"]"
fi

echo "Ensuring secret has an initial version (values are never in Terraform state)"
if ! gcloud secrets versions list "$SECRET_ID" --limit=1 --format='value(name)' 2>/dev/null | grep -q .; then
  echo -n "dev-placeholder-rotate-me" | gcloud secrets versions add "$SECRET_ID" --data-file=-
  echo "Added placeholder secret version — rotate via gcloud when ready"
else
  echo "Secret already has at least one version"
fi

echo ""
echo "Bootstrap complete. Developer next steps:"
echo "  gcloud auth login"
echo "  gcloud auth application-default login"
echo "  gcloud config set project $PROJECT_ID"
echo "  See docs/CLONE_TO_RUNNING.md"
