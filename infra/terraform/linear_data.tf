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
