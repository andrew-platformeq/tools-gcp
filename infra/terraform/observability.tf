# Pillar 2 — Observability. Created only when alert_email is set, so the default
# apply (empty tfvars) is unchanged. Email is the simplest channel; swap for a
# Slack/PagerDuty channel later without touching the budget or alert wiring.

resource "google_monitoring_notification_channel" "ops_email" {
  count = var.alert_email == "" ? 0 : 1

  display_name = "Pēq non-prod ops alerts"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }

  depends_on = [google_project_service.apis]
}

# Tier-1 alert: any sustained 5xx from the Cloud Run service. The threshold is
# intentionally aggressive for non-prod (rate > 0 over 5m); tune for prod. The
# service need not be Terraform-managed — this matches it by name via labels.
resource "google_monitoring_alert_policy" "cloud_run_5xx" {
  count = var.alert_email == "" ? 0 : 1

  display_name = "Cloud Run 5xx — ${var.app_name}"
  combiner     = "OR"

  conditions {
    display_name = "5xx response rate > 0"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${var.app_name}\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.labels.response_code_class = \"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "300s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.ops_email[0].id]

  depends_on = [google_project_service.apis]
}
