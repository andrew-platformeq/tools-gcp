# Linear medallion data platform — bucket, BigQuery datasets, ingest secret, IAM.
# Silver/Gold SQL lives in infra/bigquery/linear/; values never in Terraform state.

resource "google_storage_bucket" "linear_data" {
  name          = "${var.project_id}-linear-data"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "linear"
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "linear_bronze" {
  dataset_id = "linear_bronze"
  location   = var.region

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "linear"
    layer       = "bronze"
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "linear_silver" {
  dataset_id = "linear_silver"
  location   = var.region

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "linear"
    layer       = "silver"
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "linear_gold" {
  dataset_id = "linear_gold"
  location   = var.region

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "linear"
    layer       = "gold"
  }

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "linear_sandbox" {
  dataset_id                  = "linear_sandbox"
  location                    = var.region
  default_table_expiration_ms = 7776000000 # 90 days — scratch tables auto-expire

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    domain      = "linear"
    layer       = "sandbox"
  }

  depends_on = [google_project_service.apis]
}

# FOLLOW-UP (tracked, not implemented here): the ingest secret currently holds a
# *personal* Linear API key. Plan to migrate to a Linear OAuth app
# (actor=application, read-only scopes) — or an interim dedicated read-only Guest bot
# account — so the pipeline identity is decoupled from any human and the audit trail
# is clean. Do this before external/customer data raises the governance bar.
resource "google_secret_manager_secret" "linear_ingest_config" {
  secret_id = "${var.project_id}-linear-ingest-config"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    job         = "linear-ingest"
  }

  depends_on = [google_project_service.apis]
}

# Cloud Run runtime SA — linear ingest + future silver sync.
resource "google_storage_bucket_iam_member" "cloud_run_linear_data" {
  bucket = google_storage_bucket.linear_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_bigquery_dataset_iam_member" "cloud_run_linear_bronze" {
  dataset_id = google_bigquery_dataset.linear_bronze.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_bigquery_dataset_iam_member" "cloud_run_linear_silver" {
  dataset_id = google_bigquery_dataset.linear_silver.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_bigquery_dataset_iam_member" "cloud_run_linear_gold" {
  dataset_id = google_bigquery_dataset.linear_gold.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_linear_ingest" {
  secret_id = google_secret_manager_secret.linear_ingest_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_secret_manager_secret_iam_member" "dev_linear_ingest_accessor" {
  for_each = local.developers

  secret_id = google_secret_manager_secret.linear_ingest_config.id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

resource "google_storage_bucket_iam_member" "dev_linear_data_object_admin" {
  for_each = local.developers

  bucket = google_storage_bucket.linear_data.name
  role   = "roles/storage.objectAdmin"
  member = each.value
}

# --- Human data access ---
# Developers (Andrew) read all medallion layers; analysts (Leo) read silver+gold only.
# Writes to bronze/silver/gold stay with the Cloud Run SA — humans never write there.
resource "google_bigquery_dataset_iam_member" "dev_linear_bronze_viewer" {
  for_each   = local.developers
  dataset_id = google_bigquery_dataset.linear_bronze.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = each.value
}

resource "google_bigquery_dataset_iam_member" "dev_linear_silver_viewer" {
  for_each   = local.developers
  dataset_id = google_bigquery_dataset.linear_silver.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = each.value
}

resource "google_bigquery_dataset_iam_member" "dev_linear_gold_viewer" {
  for_each   = local.developers
  dataset_id = google_bigquery_dataset.linear_gold.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = each.value
}

resource "google_bigquery_dataset_iam_member" "analyst_linear_silver_viewer" {
  for_each   = local.analysts
  dataset_id = google_bigquery_dataset.linear_silver.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = each.value
}

resource "google_bigquery_dataset_iam_member" "analyst_linear_gold_viewer" {
  for_each   = local.analysts
  dataset_id = google_bigquery_dataset.linear_gold.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = each.value
}

# Shared sandbox: both developers and analysts get read/write (analysis/testing scratch).
resource "google_bigquery_dataset_iam_member" "dev_linear_sandbox_editor" {
  for_each   = local.developers
  dataset_id = google_bigquery_dataset.linear_sandbox.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = each.value
}

resource "google_bigquery_dataset_iam_member" "analyst_linear_sandbox_editor" {
  for_each   = local.analysts
  dataset_id = google_bigquery_dataset.linear_sandbox.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = each.value
}

resource "google_cloud_run_v2_job" "linear_ingest" {
  name     = "linear-ingest"
  location = var.region
  project  = var.project_id

  template {
    template {
      service_account = google_service_account.cloud_run.email
      timeout         = "3600s"
      max_retries     = 0

      containers {
        image   = local.container_image
        command = ["tools-linear-ingest"]

        env {
          name  = "TOOLS_GCP_PROJECT"
          value = var.project_id
        }
        env {
          name  = "TOOLS_GCP_REGION"
          value = var.region
        }
        env {
          name  = "TOOLS_LINEAR_INGEST_SECRET_NAME"
          value = google_secret_manager_secret.linear_ingest_config.secret_id
        }
        env {
          name  = "TOOLS_LINEAR_DATA_BUCKET"
          value = google_storage_bucket.linear_data.name
        }
      }
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_cloud_run_v2_job_iam_member" "linear_ingest_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.linear_ingest.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_run.email}"
}
