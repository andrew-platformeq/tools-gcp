# Dev sandbox bucket — force_destroy is intentional for non-prod scratch data only.
# Do NOT use force_destroy on medallion or production data buckets.
resource "google_storage_bucket" "dev_sandbox" {
  name          = "${var.project_id}-dev-sandbox"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  depends_on = [google_project_service.apis]
}

# Secret container only — values are added via gcloud, never stored in Terraform state.
resource "google_secret_manager_secret" "app_config" {
  secret_id = "${var.project_id}-app-config"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  depends_on = [google_project_service.apis]
}

resource "google_service_account" "cloud_run" {
  account_id   = "${var.app_name}-run"
  display_name = "Cloud Run runtime for ${var.app_name}"
}

resource "google_artifact_registry_repository" "app" {
  location      = var.region
  repository_id = var.app_name
  format        = "DOCKER"
  description   = "Container images for ${var.app_name}"

  depends_on = [google_project_service.apis]
}
