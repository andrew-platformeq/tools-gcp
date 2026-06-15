#!/usr/bin/env python3
"""Generate the GCP setup walkthrough PDF (max ~15 pages)."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "tools-gcp-setup-walkthrough.pdf"


class SetupPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "tools-gcp - GCP Setup Walkthrough", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section(self, title: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def subsection(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.2, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.2, f"  -  {text}", new_x="LMARGIN", new_y="NEXT")

    def code(self, text: str) -> None:
        self.set_font("Courier", "", 8.5)
        self.set_text_color(20, 20, 20)
        self.set_fill_color(245, 245, 245)
        for line in text.strip().splitlines():
            self.cell(0, 4.8, f"  {line}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

    def table_row(self, c1: str, c2: str) -> None:
        self.set_font("Helvetica", "B", 9)
        x, y = self.get_x(), self.get_y()
        self.multi_cell(52, 5.2, c1)
        self.set_xy(x + 52, y)
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 5.2, c2, new_x="LMARGIN", new_y="NEXT")


def build_pdf() -> None:
    pdf = SetupPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 60, 120)
    pdf.ln(18)
    pdf.multi_cell(0, 10, "tools-gcp", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 8, "GCP Non-Prod Setup Walkthrough", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        6,
        "A detailed record of how tools-non-prod was stood up: org admin steps, "
        "Terraform bootstrap, local testing, Cloud Run deploy, and fixes applied along the way.",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(14)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "Project: tools-non-prod  |  Region: us-central1  |  June 2026", align="C")

    # 1. Executive summary
    pdf.add_page()
    pdf.section("1. Executive Summary")
    pdf.body(
        "This document describes the end-to-end setup of the Peq non-prod GCP platform. "
        "The repository provides a minimal FastAPI service, Terraform infrastructure, "
        "and runbooks so a developer can clone the repo, authenticate without key files, "
        "run locally against Secret Manager, and deploy to authenticated Cloud Run."
    )
    pdf.body(
        "Setup was completed successfully in June 2026. All Phase 1 acceptance checks pass: "
        "make ci, make verify, local /health and /ready, terraform plan (no drift), "
        "make deploy, and make smoke against the live Cloud Run service."
    )
    pdf.subsection("Outcome")
    pdf.bullet("GCP project tools-non-prod created under platformeq.com org with billing linked")
    pdf.bullet("23+ Terraform resources applied (APIs, buckets, secret container, IAM, audit logging)")
    pdf.bullet("Terraform state migrated to gs://tools-non-prod-terraform-state")
    pdf.bullet("Secret tools-non-prod-app-config has a placeholder version (not in Terraform state)")
    pdf.bullet("Cloud Run service tools-gcp deployed and reachable with gcloud identity token")
    pdf.bullet("Cloud Build IAM fixed so make deploy works without manual gcloud IAM commands")

    pdf.subsection("Design principles enforced")
    pdf.bullet("No service account key JSON files on developer machines or in git")
    pdf.bullet("Secret values only in Secret Manager; Terraform manages containers only")
    pdf.bullet("IAM scoped to specific buckets, secrets, and registry  - not whole-project storage access")
    pdf.bullet("Cloud Run deployed with --no-allow-unauthenticated")

    # 2. Roles and prerequisites
    pdf.add_page()
    pdf.section("2. Roles, Prerequisites, and Project Creation")
    pdf.subsection("Org admin (Joe)  - one-time steps")
    pdf.body(
        "Before any developer could run Terraform, the empty GCP project had to exist, "
        "billing had to be linked, and the developer needed Owner on the project."
    )
    pdf.bullet("Create project with Project ID exactly tools-non-prod (must match Terraform)")
    pdf.bullet("Project display name: Peq Non-Prod; placed under company org folder")
    pdf.bullet("Link corporate billing account to the project")
    pdf.bullet("Grant user:andrew@platformeq.com the Owner role on tools-non-prod")
    pdf.body(
        "Owner (or Editor) is required for the first terraform apply: enabling APIs, "
        "creating buckets, binding IAM, and creating service accounts."
    )

    pdf.subsection("Developer machine prerequisites")
    pdf.table_row("Tool", "Purpose")
    pdf.table_row("gcloud CLI", "Auth, deploy, secret admin")
    pdf.table_row("Terraform >= 1.5", "Infrastructure apply (v1.15.6 used)")
    pdf.table_row("Python 3.11+", "Local dev and tests")
    pdf.table_row("Docker", "Optional locally; Cloud Build builds images in GCP")

    pdf.subsection("Authentication setup")
    pdf.body("Two auth layers are required  - they serve different purposes:")
    pdf.bullet("gcloud auth login  - user identity for deploy, project admin, smoke tests")
    pdf.bullet("gcloud auth application-default login  - ADC for Python Secret Manager client")
    pdf.bullet("gcloud config set project tools-non-prod")
    pdf.bullet("gcloud auth application-default set-quota-project tools-non-prod")
    pdf.body(
        "After renaming the project from an earlier placeholder (platformeq-nonprod), "
        "ADC had to be re-logged in so the quota project matched tools-non-prod. "
        "make verify confirms 12 checks including auth and tooling."
    )

    # 3. Repository and security hardening
    pdf.add_page()
    pdf.section("3. Repository Foundation and Security Hardening")
    pdf.body(
        "Before GCP bootstrap, the repository was prepared with application code, Terraform, "
        "CI, and documentation. A security review drove several infrastructure improvements."
    )
    pdf.subsection("Application layer")
    pdf.bullet("FastAPI app with /health (config echo) and /ready (Secret Manager probe)")
    pdf.bullet("config.py reads non-secret env vars only; secrets.py uses ADC")
    pdf.bullet("TOOLS_SKIP_GCP=1 for tests; make ci runs lint, pip-audit, and 3 unit tests")

    pdf.subsection("Terraform security changes (pre-bootstrap)")
    pdf.bullet("Removed google_secret_manager_secret_version  - no secret values in state")
    pdf.bullet("Resource-scoped IAM: dev bucket, state bucket, one secret, one registry repo")
    pdf.bullet("GCS remote state bucket with versioning; local override for first apply only")
    pdf.bullet("Secret Manager DATA_READ audit logging enabled")
    pdf.bullet("Optional org policies for SA key blocking (enforce_no_sa_keys; left false initially)")
    pdf.bullet("Provider upgraded to google ~> 6.0; .terraform.lock.hcl committed")

    pdf.subsection("Operations hardening")
    pdf.bullet("Dockerfile: non-root user, base image pinned by digest")
    pdf.bullet("make deploy uses --no-allow-unauthenticated; make smoke uses identity token")
    pdf.bullet("Dependabot for pip and GitHub Actions; pip-audit in CI")
    pdf.bullet("make ci target mirrors GitHub Actions locally")

    # 4. Terraform bootstrap
    pdf.add_page()
    pdf.section("4. Terraform Bootstrap (Manual Path  - Option A)")
    pdf.body(
        "bootstrap-project.sh is designed for org admins creating a project from scratch. "
        "Because Joe had already created tools-non-prod and linked billing, the manual "
        "Terraform path was used instead."
    )
    pdf.subsection("terraform.tfvars")
    pdf.code(
        """project_id  = "tools-non-prod"
region      = "us-central1"
member      = "user:andrew@platformeq.com"
environment = "nonprod"
app_name    = "tools-gcp"
enforce_no_sa_keys = false"""
    )
    pdf.subsection("First apply  - local state")
    pdf.body(
        "Terraform declares backend \"gcs\" {} but the state bucket does not exist until "
        "after the first apply. Terraform 1.15 cannot run plan after init -backend=false. "
        "Solution: copy local_backend_override.tf.example to local_backend_override.tf "
        "which overrides the backend to local for the first run only."
    )
    pdf.code(
        """cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
cp local_backend_override.tf.example local_backend_override.tf
terraform init -reconfigure
terraform plan    # Plan: 23 to add
terraform apply   # Apply complete: 23 added"""
    )

    pdf.subsection("Resources created (23 initial resources)")
    pdf.bullet("8 APIs enabled (Run, Secret Manager, Storage, BigQuery, AR, Cloud Build, IAM, Org Policy)")
    pdf.bullet("Buckets: tools-non-prod-dev-sandbox (force_destroy) and tools-non-prod-terraform-state (versioned)")
    pdf.bullet("Secret container tools-non-prod-app-config (no value in Terraform)")
    pdf.bullet("Service account tools-gcp-run@tools-non-prod.iam.gserviceaccount.com")
    pdf.bullet("Artifact Registry repo tools-gcp in us-central1")
    pdf.bullet("Scoped IAM for developer and Cloud Run runtime")

    # 5. State migration and secrets
    pdf.add_page()
    pdf.section("5. State Migration, Secret Version, and Local Testing")
    pdf.subsection("Migrate state to GCS")
    pdf.body(
        "After the first apply, local_backend_override.tf is deleted and state is migrated "
        "to the bucket Terraform just created. This makes infrastructure state shared and durable."
    )
    pdf.code(
        """rm local_backend_override.tf
cp backend.hcl.example backend.hcl
# bucket = "tools-non-prod-terraform-state"
terraform init -backend-config=backend.hcl -migrate-state"""
    )

    pdf.subsection("Add secret value (outside Terraform)")
    pdf.code(
        'echo -n "dev-placeholder-rotate-me" | gcloud secrets versions add tools-non-prod-app-config --data-file=-'
    )
    pdf.body(
        "This aligns with SECRETS.md: Terraform owns the secret container; humans or gcloud "
        "own the values. Rotate the placeholder when real config is available."
    )

    pdf.subsection("Local application test")
    pdf.code(
        """cp .env.example .env   # no TOOLS_SKIP_GCP
make dev
curl http://localhost:8080/health
curl http://localhost:8080/ready"""
    )
    pdf.body("Verified responses:")
    pdf.bullet('/health: {"status":"ok","project":"tools-non-prod","environment":"nonprod"}')
    pdf.bullet('/ready: {"status":"ready","secret_configured":true}')

    # 6. Cloud Build fix
    pdf.add_page()
    pdf.section("6. Cloud Build Deploy Fix")
    pdf.body(
        "make deploy runs gcloud builds submit then gcloud run deploy. The first deploy "
        "attempts failed because Terraform had granted deploy-related permissions to the "
        "developer user but not to the service accounts that actually execute builds."
    )
    pdf.subsection("Error 1  - staging bucket access")
    pdf.body(
        "gcloud uploads source to gs://tools-non-prod_cloudbuild/. The default compute "
        "service account (894268831911-compute@developer.gserviceaccount.com) lacked "
        "storage.objects.get on that bucket."
    )
    pdf.subsection("Error 2  - Artifact Registry push")
    pdf.body(
        "The build succeeded but pushing the image failed with "
        "artifactregistry.repositories.uploadArtifacts denied. The same compute SA "
        "needed artifactregistry.writer on the tools-gcp repository."
    )

    pdf.subsection("Terraform fix  - cloudbuild.tf")
    pdf.body("Added infra/terraform/cloudbuild.tf with scoped IAM:")
    pdf.bullet("storage.objectAdmin on tools-non-prod_cloudbuild for Cloud Build SA and compute SA")
    pdf.bullet("artifactregistry.writer on tools-gcp repo for both SAs")
    pdf.bullet("logging.logWriter at project level for build logs")
    pdf.body(
        "After terraform apply (+6 IAM resources), make deploy completed successfully. "
        "Image: us-central1-docker.pkg.dev/tools-non-prod/tools-gcp/tools-gcp:latest"
    )

    # 7. Cloud Run deploy and verification
    pdf.add_page()
    pdf.section("7. Cloud Run Deploy and Verification")
    pdf.subsection("Deploy")
    pdf.body(
        "make deploy builds via Cloud Build, pushes to Artifact Registry, and deploys "
        "Cloud Run with the runtime service account and non-secret env vars."
    )
    pdf.code(
        """gcloud run deploy tools-gcp \\
  --image us-central1-docker.pkg.dev/tools-non-prod/tools-gcp/tools-gcp:latest \\
  --service-account tools-gcp-run@tools-non-prod.iam.gserviceaccount.com \\
  --no-allow-unauthenticated \\
  --set-env-vars TOOLS_GCP_PROJECT=tools-non-prod,..."""
    )
    pdf.body("Service URL (example): https://tools-gcp-894268831911.us-central1.run.app")

    pdf.subsection("Smoke test (authenticated)")
    pdf.code("make smoke   # uses gcloud auth print-identity-token")
    pdf.body("Both /health and /ready returned HTTP 200 with the same JSON as local dev.")

    pdf.subsection("Final verification matrix")
    pdf.table_row("Check", "Result")
    pdf.table_row("make ci", "3 tests passed, ruff clean, pip-audit clean")
    pdf.table_row("make verify", "12/12 passed")
    pdf.table_row("terraform plan", "No changes  - infra matches config")
    pdf.table_row("make smoke", "/health ok, /ready secret_configured true")
    pdf.table_row("No credential files in repo", "verify-setup.sh clean")

    # 8. IAM reference
    pdf.add_page()
    pdf.section("8. IAM and Resource Reference")
    pdf.subsection("Developer (user:andrew@platformeq.com)")
    pdf.table_row("Role / binding", "Scope")
    pdf.table_row("roles/bigquery.user", "Project")
    pdf.table_row("roles/run.developer", "Project")
    pdf.table_row("roles/cloudbuild.builds.editor", "Project")
    pdf.table_row("roles/storage.objectAdmin", "tools-non-prod-dev-sandbox + terraform-state buckets")
    pdf.table_row("roles/secretmanager.secretAccessor", "tools-non-prod-app-config only")
    pdf.table_row("roles/artifactregistry.writer", "tools-gcp repo only")
    pdf.table_row("roles/iam.serviceAccountUser", "tools-gcp-run SA only")

    pdf.subsection("Cloud Run runtime SA")
    pdf.bullet("tools-gcp-run@tools-non-prod.iam.gserviceaccount.com")
    pdf.bullet("secretAccessor on tools-non-prod-app-config only; no key file")

    pdf.subsection("Cloud Build SAs (cloudbuild.tf)")
    pdf.bullet("894268831911@cloudbuild.gserviceaccount.com")
    pdf.bullet("894268831911-compute@developer.gserviceaccount.com")
    pdf.bullet("objectAdmin on _cloudbuild bucket; writer on AR repo; logWriter on project")

    pdf.subsection("Key resource names")
    pdf.table_row("Resource", "Name")
    pdf.table_row("Project ID", "tools-non-prod")
    pdf.table_row("Dev bucket", "tools-non-prod-dev-sandbox")
    pdf.table_row("State bucket", "tools-non-prod-terraform-state")
    pdf.table_row("Secret", "tools-non-prod-app-config")
    pdf.table_row("Registry", "us-central1-docker.pkg.dev/tools-non-prod/tools-gcp")

    # 9. Troubleshooting
    pdf.add_page()
    pdf.section("9. Troubleshooting Reference")
    pdf.table_row("Symptom", "Fix")
    pdf.table_row(
        "terraform plan fails after init -backend=false",
        "Use local_backend_override.tf.example; run terraform init -reconfigure",
    )
    pdf.table_row(
        "ADC quota project warning (old project ID)",
        "gcloud auth application-default login; set-quota-project tools-non-prod",
    )
    pdf.table_row(
        "/ready secret_configured false",
        "Add secret version via gcloud; confirm ADC and secretAccessor IAM",
    )
    pdf.table_row(
        "Cloud Build 403 on _cloudbuild bucket",
        "Apply cloudbuild.tf or grant compute SA storage on staging bucket",
    )
    pdf.table_row(
        "AR uploadArtifacts denied",
        "Grant compute SA artifactregistry.writer on tools-gcp repo",
    )
    pdf.table_row(
        "make smoke 403",
        "Service is authenticated; use identity token (make smoke does this)",
    )

    # 10. Phase 2
    pdf.section("10. What Is Not Done Yet (Phase 2+)")
    pdf.bullet("GitHub Workload Identity Federation for keyless CI deploy")
    pdf.bullet("Okta to GCP workforce federation")
    pdf.bullet("Cloud Run service defined in Terraform (still Makefile deploy)")
    pdf.bullet("enforce_no_sa_keys = true org policies (optional, when ready)")
    pdf.bullet("GitHub branch protection requiring lint-and-test on main")
    pdf.bullet("Billing budget alert in GCP Console")
    pdf.bullet("Medallion data layers, BigQuery datasets, healthcare pipeline")

    pdf.ln(4)
    pdf.subsection("Ongoing operations")
    pdf.bullet("make dev  - local server on :8080")
    pdf.bullet("make deploy && make smoke  - ship new revisions")
    pdf.bullet("cd infra/terraform && terraform plan  - infra changes via PR")
    pdf.bullet("docs/CLONE_TO_RUNNING.md  - onboarding checklist for new developers")

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0,
        5,
        "Generated from the completed tools-non-prod bootstrap (June 2026). "
        "Canonical runbooks: docs/GCP_SETUP.md, docs/WAITING_FOR_GCP.md, docs/CLONE_TO_RUNNING.md. "
        "Regenerate: python scripts/generate-setup-report.py",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT} ({pdf.pages_count} pages)")


if __name__ == "__main__":
    build_pdf()
