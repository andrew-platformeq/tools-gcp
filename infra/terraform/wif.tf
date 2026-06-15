# Pillar 3 — Keyless CI via Workload Identity Federation.
# GitHub Actions presents an OIDC token; GCP exchanges it for a short-lived
# token to impersonate the deployer SA. No service-account JSON key ever exists.

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions"
  description               = "Keyless CI auth for GitHub Actions"

  depends_on = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc"
  display_name                       = "GitHub OIDC"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  # Hard gate: only tokens issued to OUR repo are accepted by the provider at all.
  # Prevents any other GitHub repo from using this provider (confused-deputy).
  attribute_condition = "assertion.repository == '${var.github_repo}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  depends_on = [google_project_service.apis]
}

# Dedicated deployer identity — separate from the developer account and the
# Cloud Run runtime SA. CI assumes this and nothing else.
resource "google_service_account" "github_deployer" {
  account_id   = "github-deployer"
  display_name = "GitHub Actions deployer (keyless via WIF)"
}

# Impersonation is restricted to the main-branch subject specifically — a push to
# any other branch (or a PR/fork) produces a different `sub` and cannot assume the
# SA, even though the provider would accept the token. Defense in depth alongside
# the workflow's own `on: push: branches: [main]`.
resource "google_service_account_iam_member" "github_deployer_wif" {
  service_account_id = google_service_account.github_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principal://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/subject/repo:${var.github_repo}:ref:refs/heads/main"
}

# --- Deployer SA permissions: exactly what `make deploy` needs, nothing more ---

# Submit Cloud Build jobs.
resource "google_project_iam_member" "deployer_cloudbuild_editor" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

# serviceusage.services.use — required by `gcloud builds submit` (and other
# gcloud calls) to use project services / access the build staging bucket.
# Without it the build fails with "forbidden from accessing the bucket".
resource "google_project_iam_member" "deployer_service_usage" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

# Deploy Cloud Run revisions.
resource "google_project_iam_member" "deployer_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

# Upload build source to the Cloud Build staging bucket (local defined in cloudbuild.tf).
# storage.admin (not objectAdmin) because `gcloud builds submit` calls
# storage.buckets.get to check the bucket — a bucket-metadata permission that
# objectAdmin lacks. Scoped to this one staging bucket, not project-wide.
resource "google_storage_bucket_iam_member" "deployer_staging" {
  bucket = local.cloudbuild_bucket
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.github_deployer.email}"
}

# Push/read images in the app's Artifact Registry repo.
resource "google_artifact_registry_repository_iam_member" "deployer_writer" {
  location   = google_artifact_registry_repository.app.location
  repository = google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.github_deployer.email}"
}

# Deploy Cloud Run AS the runtime SA — scoped to that one SA, not project-wide.
resource "google_service_account_iam_member" "deployer_act_as_runtime" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_deployer.email}"
}
