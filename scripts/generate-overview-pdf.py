#!/usr/bin/env python3
"""Generate tools-gcp implementation overview PDF."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "tools-gcp-implementation-overview.pdf"


class OverviewPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "tools-gcp - Implementation Overview", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str) -> None:
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def subsection_title(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, f"  -  {text}", new_x="LMARGIN", new_y="NEXT")

    def table_row(self, col1: str, col2: str, bold_first: bool = False) -> None:
        self.set_font("Helvetica", "B" if bold_first else "", 9)
        x, y = self.get_x(), self.get_y()
        self.multi_cell(55, 5.5, col1, border=0)
        self.set_xy(x + 55, y)
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 5.5, col2, new_x="LMARGIN", new_y="NEXT")


def build_pdf() -> None:
    pdf = OverviewPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title page content
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 60, 120)
    pdf.ln(20)
    pdf.multi_cell(0, 10, "tools-gcp", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 8, "Implementation Overview", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        6,
        "A comprehensive guide to the changes made to stand up the non-prod GCP "
        "development platform: what was built, why it exists, and how the pieces fit together.",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "Phase 1 - Clone-to-Running Foundation\nJune 2026", align="C")

    pdf.add_page()

    # 1. Executive Summary
    pdf.section_title("1. Executive Summary")
    pdf.body(
        "This repository was transformed from a two-file skeleton (.gitignore and requirements.txt) "
        "into a complete non-prod development platform. The goal is auditable and testable: a developer "
        "can clone the repo, authenticate via gcloud (no credential files on disk), run a minimal "
        "application locally, and deploy it to Cloud Run - with all secret values living in GCP Secret Manager."
    )
    pdf.body(
        "This is foundational work only. It proves the platform can run something. The healthcare data "
        "pipeline (Dataproc, Composer, medallion architecture) will run on this platform later but is "
        "explicitly out of scope for Phase 1."
    )
    pdf.subsection_title("Core hypothesis")
    pdf.body(
        "With standardized Git workflow, a locked-down non-prod GCP project, and Secret Manager as the "
        "only runtime secret store (via Application Default Credentials locally and attached service "
        "accounts on Cloud Run), developers eliminate credential leakage risk on local disks while going "
        "from git clone to a live container quickly."
    )
    pdf.subsection_title("What remains blocked")
    pdf.bullet("Creation of the GCP project peq-tools (org admin / Joe)")
    pdf.bullet("Terraform apply against a live project")
    pdf.bullet("Full end-to-end acceptance pass including Cloud Run deploy")
    pdf.bullet("GitHub branch protection configuration (manual admin step in GitHub UI)")

    # 2. Architecture
    pdf.add_page()
    pdf.section_title("2. System Architecture")
    pdf.body(
        "Phase 1 uses Application Default Credentials (ADC) only. Okta-to-GCP federation and GitHub "
        "Workload Identity Federation are documented as Phase 2 follow-ups."
    )
    pdf.subsection_title("Authentication model")
    pdf.table_row("Context", "Auth mechanism", bold_first=True)
    pdf.table_row("Local dev", "gcloud auth login + gcloud auth application-default login")
    pdf.table_row("Cloud Run", "Attached service account (no key file ever downloaded)")
    pdf.table_row("CI (Phase 1)", "No GCP access - lint and unit tests only, no GitHub Secrets")
    pdf.table_row("CI (Phase 2)", "Workload Identity Federation for keyless deploy")
    pdf.ln(3)
    pdf.subsection_title("Forbidden patterns")
    pdf.bullet("Service account JSON keys on disk or in git")
    pdf.bullet(".env files containing real secret values")
    pdf.bullet("Plaintext secrets in Dockerfile or Cloud Run environment variables")
    pdf.bullet("gcloud iam service-accounts keys create in any script or doc")
    pdf.subsection_title("Data flow")
    pdf.body(
        "Developers clone the repo and run make install to create a local Python virtual environment. "
        "They authenticate with gcloud, which stores credentials in the OS keychain - not in the repo. "
        "The application reads configuration names from environment variables (project ID, region, secret "
        "name) but fetches secret values exclusively from Secret Manager via the Google Cloud SDK. "
        "When deployed, Cloud Run uses its own service account with secretmanager.secretAccessor - "
        "the same pattern, no local files."
    )

    # 3. Repository structure
    pdf.add_page()
    pdf.section_title("3. Repository Structure")
    pdf.body("The repo is organized into five logical areas:")
    pdf.subsection_title("src/tools/ - Application code")
    pdf.body(
        "Minimal FastAPI application proving Cloud Run + Secret Manager integration. Two endpoints: "
        "/health (no GCP calls, always succeeds) and /ready (proves Secret Manager is reachable via ADC). "
        "Intentionally small - not a product scaffold."
    )
    pdf.subsection_title("infra/terraform/ - Infrastructure as Code")
    pdf.body(
        "Auditable, repeatable GCP provisioning. Enables APIs, binds developer IAM, creates dev sandbox "
        "bucket, placeholder secret, Cloud Run runtime service account, and Artifact Registry repository. "
        "Applied once by org admin when the project exists."
    )
    pdf.subsection_title("docs/ - Standards and runbooks")
    pdf.body(
        "GIT_STANDARDS.md, SECRETS.md, GCP_SETUP.md, and CLONE_TO_RUNNING.md. These make the workflow "
        "auditable and give Joe/Leo/any developer a single source of truth."
    )
    pdf.subsection_title(".github/workflows/ - Continuous integration")
    pdf.body(
        "GitHub Actions workflow named lint-and-test. Runs on every push and PR to main. No GCP "
        "credentials stored in GitHub."
    )
    pdf.subsection_title("scripts/ - Automation")
    pdf.body(
        "bootstrap-project.sh for org admin one-shot project creation and Terraform apply. "
        "verify-setup.sh for developer preflight checks before the acceptance pass."
    )

    # 4. Git standards
    pdf.add_page()
    pdf.section_title("4. Git Standards and Secrets Hygiene")
    pdf.subsection_title(".gitignore (modified)")
    pdf.body(
        "The original .gitignore blocked all *.json files. This was narrowed to credential-specific "
        "patterns: *credentials*.json, *service-account*.json, *-key.json. This prevents accidental "
        "commit of service account keys while still allowing legitimate JSON files (Terraform lock files, "
        "CI configs) in the future."
    )
    pdf.body("Retained blocks: .env, .env.local, .env.*.local, .gcloud/, adc.json")
    pdf.subsection_title("docs/GIT_STANDARDS.md")
    pdf.body("Defines branch naming (feature/, fix/, chore/), PR requirements (1 approval, CI pass), "
             "Conventional Commits format, and the code review checklist including secrets verification.")
    pdf.subsection_title("docs/SECRETS.md")
    pdf.body(
        "The authoritative secrets policy. Documents the two gcloud auth commands developers must run, "
        "how Secret Manager is accessed at runtime, what is forbidden, and which environment variables "
        "are allowed (names only, never values)."
    )
    pdf.subsection_title("CONTRIBUTING.md and PR template")
    pdf.body(
        "Short entry point for contributors with links to standards docs. The PR template in "
        ".github/pull_request_template.md includes a mandatory secrets check and infra rollback section "
        "so reviewers catch credential leaks before merge."
    )
    pdf.subsection_title("Branch protection (manual step)")
    pdf.body(
        "Documented in GIT_STANDARDS.md: require PR, 1 approving review, and lint-and-test status check "
        "on main. Must be configured in GitHub Settings by a repo admin - not automatable without gh CLI access."
    )

    # 5. Terraform
    pdf.add_page()
    pdf.section_title("5. GCP Infrastructure (Terraform)")
    pdf.body(
        "All infrastructure lives in infra/terraform/. Joe (org admin) runs scripts/bootstrap-project.sh "
        "or applies Terraform manually after creating the project and linking billing."
    )
    pdf.subsection_title("APIs enabled (apis.tf)")
    pdf.bullet("Cloud Run, Secret Manager, Cloud Storage, BigQuery")
    pdf.bullet("Artifact Registry, Cloud Build, IAM")
    pdf.subsection_title("Developer IAM roles (iam.tf)")
    pdf.body("Project-scoped roles for the developer Google account (var.member):")
    pdf.bullet("roles/bigquery.user - run queries and jobs")
    pdf.bullet("roles/run.developer - deploy and invoke Cloud Run services")
    pdf.bullet("roles/storage.objectAdmin - read/write dev sandbox bucket")
    pdf.bullet("roles/secretmanager.secretAccessor - read secrets at runtime")
    pdf.bullet("roles/artifactregistry.writer - push container images")
    pdf.bullet("roles/cloudbuild.builds.editor - build images via Cloud Build")
    pdf.bullet("roles/iam.serviceAccountUser - deploy Cloud Run with attached SA")
    pdf.body(
        "The last three roles are required for make deploy to work. Without them, gcloud builds submit "
        "fails with opaque permission errors."
    )
    pdf.subsection_title("Resources created (resources.tf)")
    pdf.bullet("GCS bucket: {project_id}-dev-sandbox - dev data/artifact sandbox")
    pdf.bullet("Secret Manager secret: {project_id}-app-config - dummy placeholder value")
    pdf.bullet("Cloud Run SA: {app_name}-run@... - runtime identity, secretAccessor only")
    pdf.bullet("Artifact Registry repo: tools-gcp - Docker images for deploy")
    pdf.subsection_title("Zero admin keys policy")
    pdf.body(
        "No script or doc uses gcloud iam service-accounts keys create. Cloud Run uses attached "
        "service account identity. GCP_SETUP.md documents an audit command to verify no SA keys exist."
    )

    # 6. Application
    pdf.add_page()
    pdf.section_title("6. Minimal Application")
    pdf.subsection_title("Purpose")
    pdf.body(
        "The smallest possible app that proves the full stack: local dev, Secret Manager via ADC, "
        "Docker build, and Cloud Run deploy. Not a product - a proof surface for the clone-to-running hypothesis."
    )
    pdf.subsection_title("Endpoints")
    pdf.table_row("Endpoint", "Purpose", bold_first=True)
    pdf.table_row("GET /health", "Returns status, project ID, environment. No GCP API calls.")
    pdf.table_row("GET /ready", "Attempts Secret Manager read. Proves ADC + IAM + bootstrap secret.")
    pdf.ln(3)
    pdf.subsection_title("Key modules")
    pdf.bullet("config.py - reads non-secret env vars only (TOOLS_GCP_PROJECT, etc.)")
    pdf.bullet("secrets.py - Secret Manager client using ADC; secret_is_accessible() for /ready")
    pdf.bullet("app.py - FastAPI routes and uvicorn entry point")
    pdf.subsection_title("TOOLS_SKIP_GCP=1")
    pdf.body(
        "When set, the app skips real GCP calls. Used by unit tests and CI so pytest runs without "
        "cloud credentials. This is the pattern for all future services: mock GCP in CI, real GCP in dev/prod."
    )
    pdf.subsection_title("Packaging and tooling")
    pdf.bullet("pyproject.toml - modern Python packaging, dev deps (pytest, ruff), tools-serve entry point")
    pdf.bullet("requirements.txt - pinned runtime deps for Docker builds")
    pdf.bullet("Dockerfile - Python 3.11 slim, no secrets baked in")
    pdf.bullet("Makefile - install, dev, test, lint, verify, deploy, smoke targets")
    pdf.bullet(".env.example - documents allowed env var names with placeholder values only")
    pdf.bullet("tests/test_app.py - two unit tests, both pass with TOOLS_SKIP_GCP=1")

    # 7. CI
    pdf.add_page()
    pdf.section_title("7. CI/CD Pipeline (Phase 1)")
    pdf.body(
        "File: .github/workflows/ci.yml. Job name: lint-and-test (matches branch protection docs)."
    )
    pdf.subsection_title("What it does")
    pdf.bullet("Triggers on push and pull_request to main")
    pdf.bullet("Checks out code, sets up Python 3.11")
    pdf.bullet("Installs package in editable mode with dev dependencies")
    pdf.bullet("Runs ruff check on src/ and tests/")
    pdf.bullet("Runs pytest with TOOLS_SKIP_GCP=1 and a placeholder project ID")
    pdf.subsection_title("What it deliberately does NOT do")
    pdf.bullet("No deploy on merge")
    pdf.bullet("No GCP authentication in Actions")
    pdf.bullet("No GitHub Secrets for service account keys")
    pdf.body(
        "Phase 2 will add Workload Identity Federation for keyless deploy from CI. Phase 1 gates code "
        "quality without storing cloud credentials in GitHub."
    )

    # 8. Verification
    pdf.add_page()
    pdf.section_title("8. Verification and Acceptance")
    pdf.subsection_title("scripts/verify-setup.sh")
    pdf.body(
        "Automated preflight script developers run before the acceptance pass. Checks:"
    )
    pdf.bullet("No secret-like values in .env")
    pdf.bullet("No credential JSON files in repo root")
    pdf.bullet("No committed .gcloud/ directory")
    pdf.bullet("python3, gcloud, git installed")
    pdf.bullet("gcloud auth login active")
    pdf.bullet("Application Default Credentials configured")
    pdf.bullet("GCP project set (warning if not)")
    pdf.bullet(".venv exists (warning if not)")
    pdf.body(
        "Exits non-zero on hard failures. Encodes the no-secrets-on-disk rule as executable checks "
        "rather than relying on manual inspection."
    )
    pdf.subsection_title("docs/CLONE_TO_RUNNING.md")
    pdf.body(
        "Step-by-step acceptance checklist: clone, authenticate, verify, install, dev, test, deploy, "
        "smoke, confirm no credential files created. This is the definition of done for Phase 1."
    )
    pdf.subsection_title("docs/GCP_SETUP.md")
    pdf.body(
        "Admin runbook for Joe: project creation, Terraform apply, IAM table, zero-keys audit, rollback "
        "instructions, and explicit scope boundary (healthcare pipeline is future work)."
    )

    # 9. How it fits together
    pdf.add_page()
    pdf.section_title("9. How Everything Fits Together")
    pdf.subsection_title("Week 1 sequence")
    pdf.body("1. Developer opens PR with docs, CI, app skeleton, Terraform (no GCP needed yet)")
    pdf.body("2. Joe creates peq-tools and runs bootstrap-project.sh")
    pdf.body("3. PR merges; CI is green; branch protection enforced")
    pdf.body("4. Developer runs clone-to-running checklist")
    pdf.body("5. make deploy pushes to Cloud Run; make smoke confirms /health and /ready")
    pdf.subsection_title("Done criteria mapping")
    pdf.table_row("Requirement", "Evidence", bold_first=True)
    pdf.table_row("(a) Git standards", "Branch protection + docs + CI green on main")
    pdf.table_row("(b) Non-prod GCP + IAM", "Terraform applied + GCP_SETUP.md")
    pdf.table_row("(c) Dev sandboxes", "GCS bucket, Secret Manager dummy, Makefile")
    pdf.table_row("No secrets on disk", "verify-setup.sh + acceptance pass")
    pdf.table_row("Clone to running", "Independent dev completes CLONE_TO_RUNNING.md")
    pdf.ln(3)
    pdf.subsection_title("Phase 2 (documented, not built)")
    pdf.bullet("GitHub Workload Identity Federation - keyless CI deploy")
    pdf.bullet("Okta to GCP workforce federation")
    pdf.bullet("Org policies (iam.disableServiceAccountKeyCreation)")
    pdf.bullet("Auto-deploy on merge to main")
    pdf.bullet("Environment promotion (staging project pattern)")

    # 10. File inventory
    pdf.add_page()
    pdf.section_title("10. Complete File Inventory")
    pdf.subsection_title("Modified files")
    pdf.bullet(".gitignore - narrowed JSON blocking to credential patterns")
    pdf.bullet("requirements.txt - added FastAPI and uvicorn for the minimal app")
    pdf.subsection_title("New files - application")
    pdf.bullet("src/tools/__init__.py, config.py, secrets.py, app.py")
    pdf.bullet("tests/test_app.py")
    pdf.bullet("pyproject.toml, Dockerfile, Makefile, .env.example")
    pdf.subsection_title("New files - infrastructure")
    pdf.bullet("infra/terraform/ - versions.tf, variables.tf, apis.tf, iam.tf, resources.tf, outputs.tf")
    pdf.bullet("infra/terraform/terraform.tfvars.example, .gitignore")
    pdf.bullet("scripts/bootstrap-project.sh, scripts/verify-setup.sh")
    pdf.subsection_title("New files - documentation")
    pdf.bullet("README.md, CONTRIBUTING.md")
    pdf.bullet("docs/GIT_STANDARDS.md, docs/SECRETS.md, docs/GCP_SETUP.md, docs/CLONE_TO_RUNNING.md")
    pdf.subsection_title("New files - GitHub")
    pdf.bullet(".github/workflows/ci.yml")
    pdf.bullet(".github/pull_request_template.md")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0,
        5,
        "Generated from the tools-gcp repository implementation. "
        "For the latest runbook steps see docs/CLONE_TO_RUNNING.md in the repo.",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
