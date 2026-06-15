# Developer IAM — project-level roles where no single resource exists yet,
# plus resource-scoped bindings for bucket, secret, registry, and Cloud Run SA.

locals {
  developers = toset(var.developers)
}

# BigQuery / Cloud Run: no datasets or services in Terraform yet — project scope is fine for now.
resource "google_project_iam_member" "bigquery_user" {
  for_each = local.developers

  project = var.project_id
  role    = "roles/bigquery.user"
  member  = each.value
}

resource "google_project_iam_member" "run_developer" {
  for_each = local.developers

  project = var.project_id
  role    = "roles/run.developer"
  member  = each.value
}

resource "google_project_iam_member" "cloudbuild_editor" {
  for_each = local.developers

  project = var.project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = each.value
}

# serviceusage.services.use — required for ADC quota project and local SDK calls
# (gcloud auth application-default set-quota-project tools-non-prod).
resource "google_project_iam_member" "developer_service_usage" {
  for_each = local.developers

  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = each.value
}

# Scoped to the dev sandbox bucket only — not every bucket in the project.
resource "google_storage_bucket_iam_member" "dev_sandbox_object_admin" {
  for_each = local.developers

  bucket = google_storage_bucket.dev_sandbox.name
  role   = "roles/storage.objectAdmin"
  member = each.value
}

# Scoped to the Terraform state bucket — developers need read/write for plan/apply.
resource "google_storage_bucket_iam_member" "terraform_state_object_admin" {
  for_each = local.developers

  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.objectAdmin"
  member = each.value
}

# Scoped to the one app-config secret — not every secret in the project.
resource "google_secret_manager_secret_iam_member" "dev_secret_accessor" {
  for_each = local.developers

  secret_id = google_secret_manager_secret.app_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

# Scoped to the Artifact Registry repo created for this app.
resource "google_artifact_registry_repository_iam_member" "dev_writer" {
  for_each = local.developers

  location   = google_artifact_registry_repository.app.location
  repository = google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.writer"
  member     = each.value
}

# Scoped to the Cloud Run SA only — not act-as on every SA in the project.
resource "google_service_account_iam_member" "dev_cloud_run_sa_user" {
  for_each = local.developers

  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = each.value
}

# Cloud Run runtime: read only the app-config secret.
resource "google_secret_manager_secret_iam_member" "cloud_run_secret_accessor" {
  secret_id = google_secret_manager_secret.app_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}
