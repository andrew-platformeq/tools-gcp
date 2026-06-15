#!/usr/bin/env bash
# Clone-to-running prerequisite checks. No secrets should exist on disk.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0
warn=0

ok()   { echo -e "${GREEN}✓${NC} $1"; pass=$((pass + 1)); }
bad()  { echo -e "${RED}✗${NC} $1"; fail=$((fail + 1)); }
note() { echo -e "${YELLOW}!${NC} $1"; warn=$((warn + 1)); }

echo "=== Tools clone-to-running verification ==="
echo ""

echo "Secrets on disk:"
if [ -f .env ] && grep -qE '(password|token|key|secret)=' .env 2>/dev/null; then
  bad ".env contains values that look like secrets — use Secret Manager"
else
  ok "No .env with secret-like values (or .env absent)"
fi

cred_found=0
for f in adc.json credentials.json service-account*.json *-key.json *credentials*.json; do
  if [ -f "$f" ] 2>/dev/null; then
    bad "Credential file found: $f"
    cred_found=1
  fi
done
[ "$cred_found" -eq 0 ] && ok "No credential JSON files in repo root"

if [ -d .gcloud ]; then
  bad ".gcloud/ directory present — should not be committed"
else
  ok "No .gcloud/ directory"
fi

echo ""
echo "Tooling:"
command -v python3 >/dev/null && ok "python3 installed ($(python3 --version))" || bad "python3 not found"
command -v gcloud >/dev/null && ok "gcloud installed" || bad "gcloud not found"
command -v git >/dev/null && ok "git installed" || bad "git not found"
if command -v terraform >/dev/null; then
  ok "terraform installed ($(terraform version | head -1))"
else
  note "terraform not found — needed for bootstrap (brew tap hashicorp/tap && brew install hashicorp/tap/terraform)"
fi
if command -v docker >/dev/null; then
  ok "docker installed"
else
  note "docker not found — optional locally; make deploy uses Cloud Build"
fi

echo ""
echo "GCP authentication:"
if command -v gcloud >/dev/null; then
  if gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | grep -q .; then
    ok "gcloud user authenticated ($(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -1))"
  else
    bad "No active gcloud user — run: gcloud auth login"
  fi

  if gcloud auth application-default print-access-token >/dev/null 2>&1; then
    ok "Application Default Credentials configured"
  else
    bad "ADC not configured — run: gcloud auth application-default login"
  fi

  PROJECT=$(gcloud config get-value project 2>/dev/null || true)
  if [ -n "$PROJECT" ] && [ "$PROJECT" != "(unset)" ]; then
    ok "gcloud project set to: $PROJECT"
  else
    note "gcloud project not set — run: gcloud config set project peq-tools"
  fi
else
  bad "Skipping GCP auth checks (gcloud missing)"
fi

echo ""
echo "Python environment:"
if [ -d .venv ]; then
  ok ".venv exists"
else
  note ".venv missing — run: make install"
fi

echo ""
echo "=== Summary: ${pass} passed, ${fail} failed, ${warn} warnings ==="

if [ "$fail" -gt 0 ]; then
  exit 1
fi
