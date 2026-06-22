output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "dev_bucket" {
  value = google_storage_bucket.dev_sandbox.name
}

output "terraform_state_bucket" {
  value = google_storage_bucket.terraform_state.name
}

output "secret_name" {
  value = google_secret_manager_secret.app_config.secret_id
}

output "cloud_run_service_account" {
  value = google_service_account.cloud_run.email
}

output "artifact_registry" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app.repository_id}"
}

output "billing_budget" {
  value       = var.billing_account == "" ? null : google_billing_budget.nonprod[0].display_name
  description = "Monthly billing budget (null if billing_account not configured)."
}

output "ops_notification_channel" {
  value       = var.alert_email == "" ? null : google_monitoring_notification_channel.ops_email[0].id
  description = "Email notification channel for budget + alerts (null if alert_email not configured)."
}

output "wif_provider" {
  value       = google_iam_workload_identity_pool_provider.github.name
  description = "Full WIF provider resource name — set as workload_identity_provider in the deploy workflow."
}

output "github_deployer_sa" {
  value       = google_service_account.github_deployer.email
  description = "Deployer service account email — set as service_account in the deploy workflow."
}

output "daily_sweep_report_secret" {
  value       = google_secret_manager_secret.daily_sweep_report_config.secret_id
  description = "Secret Manager container for daily-sweep-report job credentials (JSON)."
}

output "daily_sweep_report_job" {
  value       = google_cloud_run_v2_job.daily_sweep_report.name
  description = "Cloud Run Job name for daily-sweep-report."
}

output "container_image" {
  value       = local.container_image
  description = "Shared container image used by the Cloud Run service and jobs."
}
