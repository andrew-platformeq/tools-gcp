.PHONY: install dev test lint ci verify deploy deploy-service deploy-telemetry-service deploy-job deploy-jobs deploy-all deploy-ci run-job smoke smoke-telemetry apply-bq-eml-viewer apply-bq-linear-bronze apply-bq-linear-bronze-all clean help

PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin
PROJECT_ID ?= $(shell gcloud config get-value project 2>/dev/null)
REGION ?= us-central1
SERVICE ?= tools-gcp
TELEMETRY_SERVICE ?= eml-viewer-telemetry
IMAGE ?= $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(SERVICE)/$(SERVICE):latest
RUNTIME_SA ?= $(SERVICE)-run@$(PROJECT_ID).iam.gserviceaccount.com
JOB ?=
ARGS ?=

LINEAR_DATA_BUCKET ?= peq-tools-linear-data
LINEAR_BRONZE_ENTITIES := organization teams workflow_states issue_labels users projects cycles issues comments attachments

# Per-job Cloud Run settings — extend when adding jobs.
ifeq ($(JOB),daily-sweep-report)
JOB_CMD := tools-daily-sweep-report
JOB_ENV_VARS := TOOLS_GCP_PROJECT=$(PROJECT_ID),TOOLS_GCP_REGION=$(REGION),TOOLS_DAILY_SWEEP_REPORT_SECRET_NAME=$(PROJECT_ID)-daily-sweep-report-config
endif
ifeq ($(JOB),linear-ingest)
JOB_CMD := tools-linear-ingest
JOB_ENV_VARS := TOOLS_GCP_PROJECT=$(PROJECT_ID),TOOLS_GCP_REGION=$(REGION),TOOLS_LINEAR_INGEST_SECRET_NAME=$(PROJECT_ID)-linear-ingest-config,TOOLS_LINEAR_DATA_BUCKET=$(PROJECT_ID)-linear-data
endif

help:
	@echo "Targets:"
	@echo "  install        Create venv and install dependencies"
	@echo "  dev            Run local dev server on :8080"
	@echo "  test           Run unit tests"
	@echo "  lint           Run ruff"
	@echo "  ci             Run full CI suite locally (lint + pip-audit + test)"
	@echo "  verify         Run clone-to-running prerequisite checks"
	@echo "  deploy         Build image and deploy Cloud Run service"
	@echo "  deploy-service Deploy Cloud Run service only (image must exist)"
	@echo "  deploy-telemetry-service  Deploy eml-viewer-telemetry public ingest service"
	@echo "  deploy-job     Deploy a Cloud Run Job (JOB=daily-sweep-report)"
	@echo "  deploy-jobs    Deploy all Cloud Run Jobs"
	@echo "  deploy-all     Build image, deploy service, deploy all jobs"
	@echo "  deploy-ci      Docker build/push + deploy service (for CI with WIF)"
	@echo "  run-job        Execute a Cloud Run Job (JOB=..., optional ARGS='backfill --entities organization')"
	@echo "  smoke          Hit /health on deployed Cloud Run service"
	@echo "  smoke-telemetry  Hit /health on eml-viewer-telemetry (no auth)"
	@echo "  apply-bq-eml-viewer  Create eml_viewer gold views in BigQuery"
	@echo "  apply-bq-linear-bronze ENTITY=...  Create one linear_bronze entity external table + view"
	@echo "  apply-bq-linear-bronze-all  Create linear_bronze external tables + views for all entities"
	@echo "  daily-sweep-report  Run daily Linear sweep report locally (dry-run default)"
	@echo "  linear-ingest       Run linear bronze ingest locally (incremental dry-run default)"
	@echo "  docs-daily-sweep    Generate daily-sweep-report PDF guide"
	@echo "  docs-linear-pipeline  Generate Linear pipeline executive PDF"
	@echo "  docs-linear-ingress-egress  Generate ingress/egress study PDF"

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
	$(BIN)/pip-audit -r requirements.txt
	TOOLS_GCP_PROJECT=ci-placeholder TOOLS_SKIP_GCP=1 $(BIN)/pytest -q

verify:
	@./scripts/verify-setup.sh

daily-sweep-report: install
	@if [ -f .env ]; then set -a && . ./.env && set +a; fi; \
	TOOLS_SKIP_GCP=$${TOOLS_SKIP_GCP:-1} $(BIN)/tools-daily-sweep-report --dry-run

linear-ingest: install
	@if [ -f .env ]; then set -a && . ./.env && set +a; fi; \
	TOOLS_SKIP_GCP=$${TOOLS_SKIP_GCP:-1} $(BIN)/tools-linear-ingest incremental --dry-run --entities organization

docs-daily-sweep: install
	$(BIN)/pip install fpdf2 -q
	$(BIN)/python scripts/generate-daily-sweep-report-doc.py

docs-linear-pipeline: install
	$(BIN)/pip install fpdf2 -q
	$(BIN)/python scripts/generate-linear-pipeline-overview-pdf.py

docs-linear-ingress-egress: install
	$(BIN)/pip install fpdf2 -q
	$(BIN)/python scripts/generate-linear-pipeline-ingress-egress-pdf.py

deploy: install
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud builds submit --tag "$(IMAGE)" --project "$(PROJECT_ID)"
	$(MAKE) deploy-service deploy-telemetry-service

deploy-all: install
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud builds submit --tag "$(IMAGE)" --project "$(PROJECT_ID)"
	$(MAKE) deploy-service deploy-telemetry-service deploy-jobs

# CI deploy via Docker — avoids gcloud builds submit, which 403s with WIF credentials
# on the Cloud Build staging bucket even when bucket IAM is correct.
deploy-ci:
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud auth configure-docker "$(REGION)-docker.pkg.dev" --quiet --project "$(PROJECT_ID)"
	docker build -t "$(IMAGE)" .
	docker push "$(IMAGE)"
	$(MAKE) deploy-service deploy-telemetry-service

deploy-service deploy-run:
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud run deploy "$(SERVICE)" \
		--image "$(IMAGE)" \
		--region "$(REGION)" \
		--project "$(PROJECT_ID)" \
		--platform managed \
		--no-allow-unauthenticated \
		--service-account "$(RUNTIME_SA)" \
		--set-env-vars "TOOLS_GCP_PROJECT=$(PROJECT_ID),TOOLS_GCP_REGION=$(REGION),TOOLS_SECRET_NAME=$(PROJECT_ID)-app-config,TOOLS_ENVIRONMENT=nonprod"
	@gcloud run services describe "$(SERVICE)" --region "$(REGION)" --project "$(PROJECT_ID)" --format='value(status.url)'

deploy-telemetry-service:
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud run deploy "$(TELEMETRY_SERVICE)" \
		--image "$(IMAGE)" \
		--region "$(REGION)" \
		--project "$(PROJECT_ID)" \
		--platform managed \
		--allow-unauthenticated \
		--service-account "$(RUNTIME_SA)" \
		--command "tools-eml-viewer-telemetry" \
		--set-env-vars "TOOLS_GCP_PROJECT=$(PROJECT_ID),TOOLS_GCP_REGION=$(REGION),TOOLS_ENVIRONMENT=nonprod,TOOLS_EML_VIEWER_TELEMETRY_SECRET_NAME=$(PROJECT_ID)-eml-viewer-telemetry-config,TOOLS_EML_VIEWER_BRONZE_DATASET=eml_viewer_bronze,TOOLS_EML_VIEWER_BRONZE_TABLE=events"
	@$(MAKE) bind-telemetry-public
	@echo "Telemetry ingest URL:"
	@gcloud run services describe "$(TELEMETRY_SERVICE)" --region "$(REGION)" --project "$(PROJECT_ID)" --format='value(status.url)'

# Chrome extensions cannot send GCP identity tokens — this service must allow allUsers.
# Warn-only: CI deployer SA often lacks setIamPolicy; org policy may also block allUsers.
bind-telemetry-public:
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	@gcloud run services add-iam-policy-binding "$(TELEMETRY_SERVICE)" \
		--region "$(REGION)" \
		--project "$(PROJECT_ID)" \
		--member=allUsers \
		--role=roles/run.invoker \
		|| (echo ""; \
		    echo "WARNING: Could not grant public invoker on $(TELEMETRY_SERVICE)."; \
		    echo "Deploy succeeded; extension flush needs roles/run.invoker for allUsers."; \
		    echo "Run as a project admin: make bind-telemetry-public"; \
		    echo "See docs/EML_VIEWER_TELEMETRY.md#public-access-org-policy."; \
		    exit 0)

deploy-jobs:
	$(MAKE) deploy-job JOB=daily-sweep-report
	$(MAKE) deploy-job JOB=linear-ingest

deploy-job:
	@test -n "$(JOB)" || (echo "Set JOB=... (e.g. daily-sweep-report)" && exit 1)
	@test -n "$(JOB_CMD)" || (echo "Unknown JOB: $(JOB) — add settings to Makefile" && exit 1)
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	gcloud run jobs deploy "$(JOB)" \
		--image "$(IMAGE)" \
		--region "$(REGION)" \
		--project "$(PROJECT_ID)" \
		--service-account "$(RUNTIME_SA)" \
		--command "$(JOB_CMD)" \
		--set-env-vars "$(JOB_ENV_VARS)"

run-job:
	@test -n "$(JOB)" || (echo "Set JOB=... (e.g. daily-sweep-report)" && exit 1)
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	@if [ -n "$(ARGS)" ]; then \
		CSV_ARGS=$$(echo "$(ARGS)" | tr ' ' ','); \
		gcloud run jobs execute "$(JOB)" \
			--region "$(REGION)" \
			--project "$(PROJECT_ID)" \
			--args="$$CSV_ARGS" \
			--wait; \
	else \
		gcloud run jobs execute "$(JOB)" \
			--region "$(REGION)" \
			--project "$(PROJECT_ID)" \
			--wait; \
	fi

smoke:
	@URL=$$(gcloud run services describe "$(SERVICE)" --region "$(REGION)" --project "$(PROJECT_ID)" --format='value(status.url)' 2>/dev/null); \
	test -n "$$URL" || (echo "Service not deployed" && exit 1); \
	TOKEN=$$(gcloud auth print-identity-token); \
	curl -sf -H "Authorization: Bearer $$TOKEN" "$$URL/health" | $(PYTHON) -m json.tool; \
	echo ""; \
	curl -sf -H "Authorization: Bearer $$TOKEN" "$$URL/ready" | $(PYTHON) -m json.tool

smoke-telemetry:
	@URL=$$(gcloud run services describe "$(TELEMETRY_SERVICE)" --region "$(REGION)" --project "$(PROJECT_ID)" --format='value(status.url)' 2>/dev/null); \
	test -n "$$URL" || (echo "Telemetry service not deployed" && exit 1); \
	if curl -sf "$$URL/health" | $(PYTHON) -m json.tool; then \
		echo "(public /health OK)"; \
	else \
		echo "Public /health failed (403 = org policy blocking allUsers). Trying with your GCP identity token..."; \
		TOKEN=$$(gcloud auth print-identity-token); \
		curl -sf -H "Authorization: Bearer $$TOKEN" "$$URL/health" | $(PYTHON) -m json.tool; \
		echo ""; \
		echo "Service is up but NOT publicly reachable. Extension flush will fail until"; \
		echo "allUsers has roles/run.invoker — see docs/EML_VIEWER_TELEMETRY.md#public-access-org-policy."; \
	fi

apply-bq-eml-viewer:
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	@for f in infra/bigquery/eml_viewer/gold/*.sql; do \
		echo "Applying $$f"; \
		bq query --use_legacy_sql=false --project_id="$(PROJECT_ID)" < "$$f"; \
	done

# Apply one entity's bronze external table (run-folder URIs discovered from GCS) + view.
# Usage: make apply-bq-linear-bronze ENTITY=issues
apply-bq-linear-bronze:
	@test -n "$(ENTITY)" || (echo "Set ENTITY=... (e.g. issues)" && exit 1)
	@test -n "$(PROJECT_ID)" || (echo "Set PROJECT_ID or gcloud config project" && exit 1)
	@URIS=$$(gsutil ls -d "gs://$(LINEAR_DATA_BUCKET)/bronze/*/run_*/$(ENTITY)/" 2>/dev/null \
		| sed 's|$$|page_*.json|' \
		| sed "s/^/'/; s/$$/'/" \
		| paste -sd, -); \
	test -n "$$URIS" || (echo "No bronze paths for $(ENTITY) under gs://$(LINEAR_DATA_BUCKET)/bronze/" && exit 1); \
	echo "Applying $(ENTITY)_pages ($$(echo "$$URIS" | tr ',' '\n' | wc -l | tr -d ' ') run URI(s))"; \
	sed "s|__GCS_URIS__|$$URIS|" infra/bigquery/linear/bronze/$(ENTITY)_pages.sql \
		| bq query --use_legacy_sql=false --project_id="$(PROJECT_ID)"
	@echo "Applying infra/bigquery/linear/bronze/$(ENTITY).sql"
	@bq query --use_legacy_sql=false --project_id="$(PROJECT_ID)" \
		< infra/bigquery/linear/bronze/$(ENTITY).sql

# Apply the bronze external table + view for every Linear entity.
apply-bq-linear-bronze-all:
	@for e in $(LINEAR_BRONZE_ENTITIES); do \
		$(MAKE) --no-print-directory apply-bq-linear-bronze ENTITY=$$e || exit 1; \
	done

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
