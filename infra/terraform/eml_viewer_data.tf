# EML Viewer telemetry — BigQuery bronze/gold, ingest secret, public Cloud Run service.
# Silver is omitted: events are append-only usage logs, not entity snapshots.

resource "google_bigquery_dataset" "eml_viewer_bronze" {
  dataset_id = "eml_viewer_bronze"
  location   = var.region

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "eml-viewer"
    layer       = "bronze"
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "eml_viewer_gold" {
  dataset_id = "eml_viewer_gold"
  location   = var.region

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "eml-viewer"
    layer       = "gold"
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_table" "eml_viewer_events" {
  dataset_id = google_bigquery_dataset.eml_viewer_bronze.dataset_id
  table_id   = "events"
  project    = var.project_id

  schema = jsonencode([
    { name = "event_id", type = "STRING", mode = "REQUIRED" },
    { name = "ingested_at", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "event", type = "STRING", mode = "REQUIRED" },
    { name = "ts", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "user_email", type = "STRING", mode = "NULLABLE" },
    { name = "identity_source", type = "STRING", mode = "NULLABLE" },
    { name = "install_id", type = "STRING", mode = "NULLABLE" },
    { name = "session_id", type = "STRING", mode = "NULLABLE" },
    { name = "extension_version", type = "STRING", mode = "NULLABLE" },
    { name = "chrome_version", type = "STRING", mode = "NULLABLE" },
    { name = "platform", type = "STRING", mode = "NULLABLE" },
    { name = "properties", type = "JSON", mode = "NULLABLE" },
  ])

  time_partitioning {
    type  = "DAY"
    field = "ingested_at"
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "eml-viewer"
    layer       = "bronze"
  }

  depends_on = [google_bigquery_dataset.eml_viewer_bronze]
}

resource "google_secret_manager_secret" "eml_viewer_telemetry_config" {
  secret_id = "${var.project_id}-eml-viewer-telemetry-config"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    service     = "eml-viewer-telemetry"
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset_iam_member" "cloud_run_eml_viewer_bronze" {
  dataset_id = google_bigquery_dataset.eml_viewer_bronze.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_bigquery_dataset_iam_member" "cloud_run_eml_viewer_gold" {
  dataset_id = google_bigquery_dataset.eml_viewer_gold.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_eml_viewer_telemetry" {
  secret_id = google_secret_manager_secret.eml_viewer_telemetry_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_secret_manager_secret_iam_member" "dev_eml_viewer_telemetry_accessor" {
  for_each = local.developers

  secret_id = google_secret_manager_secret.eml_viewer_telemetry_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

resource "google_bigquery_dataset_iam_member" "dev_eml_viewer_bronze" {
  for_each = local.developers

  dataset_id = google_bigquery_dataset.eml_viewer_bronze.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = each.value
}

resource "google_bigquery_dataset_iam_member" "dev_eml_viewer_gold" {
  for_each = local.developers

  dataset_id = google_bigquery_dataset.eml_viewer_gold.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = each.value
}

# Cloud Run service is deployed via `make deploy-telemetry-service` (same pattern as
# tools-gcp). Terraform owns data plane + secret only. Deletion protection is not
# set here — gcloud run deploy has no --deletion-protection flag; use IAM + process.
