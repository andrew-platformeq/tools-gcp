# Pillar 1 — Financial guardrail. A hard spending threshold with email alerts.
# Created only when billing_account is set. NOTE: applying this needs
# billing-account-level permission (roles/billing.budgets.editor or Billing
# Account Admin) — typically the org/billing admin, NOT the project-scoped
# developer account. If `terraform apply` fails here with a permission error,
# that's expected: hand this resource to whoever holds billing admin.

data "google_project" "this" {
  count      = var.billing_account == "" ? 0 : 1
  project_id = var.project_id
}

resource "google_billing_budget" "nonprod" {
  count = var.billing_account == "" ? 0 : 1

  billing_account = var.billing_account
  display_name    = "${var.project_id} monthly budget"

  budget_filter {
    projects = ["projects/${data.google_project.this[0].number}"]
  }

  amount {
    specified_amount {
      # currency_code must match the billing account's currency.
      currency_code = "USD"
      units         = tostring(var.budget_amount)
    }
  }

  # Alert at 50% / 90% / 100% of actual spend, plus 100% of forecasted spend.
  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.9
  }
  threshold_rules {
    threshold_percent = 1.0
  }
  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "FORECASTED_SPEND"
  }

  # Email the ops channel (if configured) on top of the default billing admins.
  all_updates_rule {
    monitoring_notification_channels = var.alert_email == "" ? [] : [google_monitoring_notification_channel.ops_email[0].id]
    disable_default_iam_recipients   = false
  }

  depends_on = [google_project_service.apis]
}
