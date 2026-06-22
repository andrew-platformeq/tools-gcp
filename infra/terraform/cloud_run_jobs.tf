# Cloud Run Jobs — batch workloads using the shared container image.
# Image tag is updated by `make deploy-job`; Terraform owns job shape and IAM.

locals {
  container_image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.app_name}/${var.app_name}:latest"
}

resource "google_cloud_run_v2_job" "daily_sweep_report" {
  name     = "daily-sweep-report"
  location = var.region
  project  = var.project_id

  template {
    template {
      service_account = google_service_account.cloud_run.email
      timeout         = "600s"
      max_retries     = 1

      containers {
        image   = local.container_image
        command = ["tools-daily-sweep-report"]

        env {
          name  = "TOOLS_GCP_PROJECT"
          value = var.project_id
        }
        env {
          name  = "TOOLS_GCP_REGION"
          value = var.region
        }
        env {
          name  = "TOOLS_DAILY_SWEEP_REPORT_SECRET_NAME"
          value = google_secret_manager_secret.daily_sweep_report_config.secret_id
        }
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Scheduler uses the runtime SA to call :run on the job.
resource "google_cloud_run_v2_job_iam_member" "daily_sweep_report_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.daily_sweep_report.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Mon–Fri 9:00 AM Eastern. Opt-in until the job secret is populated and validated.
resource "google_cloud_scheduler_job" "daily_sweep_report" {
  count = var.enable_daily_sweep_scheduler ? 1 : 0

  name        = "daily-sweep-report"
  description = "Run daily Linear sweep report email"
  schedule    = "0 9 * * 1-5"
  time_zone   = "America/New_York"
  region      = var.region
  project     = var.project_id

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/jobs/${google_cloud_run_v2_job.daily_sweep_report.name}:run"

    oauth_token {
      service_account_email = google_service_account.cloud_run.email
    }
  }

  depends_on = [
    google_project_service.apis,
    google_service_account_iam_member.scheduler_daily_sweep_sa_user[0],
  ]
}

# Cloud Scheduler must act as the runtime SA to mint the OAuth token for :run.
resource "google_service_account_iam_member" "scheduler_daily_sweep_sa_user" {
  count = var.enable_daily_sweep_scheduler ? 1 : 0

  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-cloudscheduler.iam.gserviceaccount.com"
}
