# Enable DATA_READ audit logs for Secret Manager so secret access is actually logged.
# Admin operations are logged by default; reads are not until this is configured.

resource "google_project_iam_audit_config" "secretmanager_data_access" {
  project = var.project_id
  service = "secretmanager.googleapis.com"

  audit_log_config {
    log_type = "DATA_READ"
  }
}
