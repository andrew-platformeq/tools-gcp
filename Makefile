.PHONY: install dev test lint ci verify deploy smoke clean help

PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin
PROJECT_ID ?= $(shell gcloud config get-value project 2>/dev/null)
REGION ?= us-central1
SERVICE ?= tools-gcp
IMAGE ?= $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(SERVICE)/$(SERVICE):latest

help:
	@echo "Targets:"
	@echo "  install   Create venv and install dependencies"
	@echo "  dev       Run local dev server on :8080"
	@echo "  test      Run unit tests"
	@echo "  lint      Run ruff"
	@echo "  ci        Run full CI suite locally (lint + pip-audit + test)"
	@echo "  verify    Run clone-to-running prerequisite checks"
	@echo "  deploy    Build and deploy to Cloud Run"
	@echo "  deploy-ci Docker build/push + deploy (for CI with WIF)"
	@echo "  smoke     Hit /health on deployed Cloud Run service"
	@echo "  daily-sweep-report  Run daily Linear sweep report (dry-run with TOOLS_SKIP_GCP=1)"
	@echo "  docs-daily-sweep    Generate daily-sweep-report PDF guide"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"

install: $(VENV)/bin/activate

dev: install
	@if [ -f .env ]; then set -a && . ./.env && set +a; fi; \
	$(BIN)/tools-serve

test: install
	TOOLS_SKIP_GCP=1 $(BIN)/pytest -q

lint: install
	$(BIN)/ruff check src tests

ci: install
	$(BIN)/ruff check src tests
	$(BIN)/pip install pip-audit -q
	$(BIN)/pip-audit
	TOOLS_GCP_PROJECT=ci-placeholder TOOLS_SKIP_GCP=1 $(BIN)/pytest -q

verify:
	@./scripts/verify-setup.sh

daily-sweep-report: install
	@if [ -f .env ]; then set -a && . ./.env && set +a; fi; \
	TOOLS_SKIP_GCP=$${TOOLS_SKIP_GCP:-1} $(BIN)/tools-daily-sweep-report --dry-run

docs-daily-sweep: install
	$(BIN)/pip install fpdf2 -q
	$(BIN)/python scripts/generate-daily-sweep-report-doc.py

deploy: install
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud builds submit --tag "$(IMAGE)" --project "$(PROJECT_ID)"
	$(MAKE) deploy-run

# CI deploy via Docker — avoids gcloud builds submit, which 403s with WIF credentials
# on the Cloud Build staging bucket even when bucket IAM is correct.
deploy-ci:
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud auth configure-docker "$(REGION)-docker.pkg.dev" --quiet --project "$(PROJECT_ID)"
	docker build -t "$(IMAGE)" .
	docker push "$(IMAGE)"
	$(MAKE) deploy-run

deploy-run:
	gcloud run deploy "$(SERVICE)" \
		--image "$(IMAGE)" \
		--region "$(REGION)" \
		--project "$(PROJECT_ID)" \
		--platform managed \
		--no-allow-unauthenticated \
		--service-account "$(SERVICE)-run@$(PROJECT_ID).iam.gserviceaccount.com" \
		--set-env-vars "TOOLS_GCP_PROJECT=$(PROJECT_ID),TOOLS_GCP_REGION=$(REGION),TOOLS_SECRET_NAME=$(PROJECT_ID)-app-config,TOOLS_ENVIRONMENT=nonprod"
	@gcloud run services describe "$(SERVICE)" --region "$(REGION)" --project "$(PROJECT_ID)" --format='value(status.url)'

smoke:
	@URL=$$(gcloud run services describe "$(SERVICE)" --region "$(REGION)" --project "$(PROJECT_ID)" --format='value(status.url)' 2>/dev/null); \
	test -n "$$URL" || (echo "Service not deployed" && exit 1); \
	TOKEN=$$(gcloud auth print-identity-token); \
	curl -sf -H "Authorization: Bearer $$TOKEN" "$$URL/health" | $(PYTHON) -m json.tool; \
	echo ""; \
	curl -sf -H "Authorization: Bearer $$TOKEN" "$$URL/ready" | $(PYTHON) -m json.tool

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
