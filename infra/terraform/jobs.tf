# Job-specific secret containers — values added via gcloud, never in Terraform state.

resource "google_secret_manager_secret" "daily_sweep_report_config" {
  secret_id = "${var.project_id}-daily-sweep-report-config"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    job         = "daily-sweep-report"
  }

  depends_on = [google_project_service.apis]
}

# Cloud Run runtime SA reads job secrets at execution time.
resource "google_secret_manager_secret_iam_member" "cloud_run_daily_sweep_report" {
  secret_id = google_secret_manager_secret.daily_sweep_report_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Developers can read/write job secret values during local dev.
resource "google_secret_manager_secret_iam_member" "dev_daily_sweep_report_accessor" {
  for_each = local.developers

  secret_id = google_secret_manager_secret.daily_sweep_report_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}
