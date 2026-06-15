# Cloud Build IAM — gcloud builds submit uses the default Compute Engine SA and/or
# the Cloud Build SA. Scoped to the Cloud Build staging bucket and app registry only.
# The staging bucket ({project_id}_cloudbuild) is auto-created by Cloud Build on first submit.

data "google_project" "current" {
  project_id = var.project_id
}

locals {
  cloudbuild_bucket = "${var.project_id}_cloudbuild"
  cloudbuild_sa     = "${data.google_project.current.number}@cloudbuild.gserviceaccount.com"
  compute_sa        = "${data.google_project.current.number}-compute@developer.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "cloudbuild_sa_staging" {
  bucket = local.cloudbuild_bucket
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${local.cloudbuild_sa}"
}

resource "google_storage_bucket_iam_member" "compute_sa_staging" {
  bucket = local.cloudbuild_bucket
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${local.compute_sa}"
}

resource "google_artifact_registry_repository_iam_member" "cloudbuild_sa_writer" {
  location   = google_artifact_registry_repository.app.location
  repository = google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${local.cloudbuild_sa}"
}

resource "google_artifact_registry_repository_iam_member" "compute_sa_writer" {
  location   = google_artifact_registry_repository.app.location
  repository = google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${local.compute_sa}"
}

resource "google_project_iam_member" "cloudbuild_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${local.cloudbuild_sa}"
}

resource "google_project_iam_member" "compute_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${local.compute_sa}"
}
