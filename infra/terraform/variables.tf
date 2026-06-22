variable "project_id" {
  description = "GCP project ID for non-prod"
  type        = string
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-central1"
}

variable "developers" {
  description = "IAM members with scoped developer access (e.g. user:andrew@platformeq.com)"
  type        = list(string)
}

variable "environment" {
  description = "Environment label"
  type        = string
  default     = "nonprod"
}

variable "app_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "tools-gcp"
}

variable "enforce_no_sa_keys" {
  description = "Enforce org policies blocking SA key creation and upload. Requires the project to be under a GCP organization."
  type        = bool
  default     = false
}

variable "alert_email" {
  description = "Email for budget + operational alerts. Leave blank to skip the notification channel and Cloud Run alert policy."
  type        = string
  default     = ""
}

variable "billing_account" {
  description = "Billing account ID (e.g. 01ABCD-2345EF-6789GH). When set, a billing budget is created. Applying it needs billing-account admin rights (roles/billing.budgets.editor) — usually the org/billing admin, not the developer account. Leave blank to skip the budget."
  type        = string
  default     = ""
}

variable "budget_amount" {
  description = "Monthly budget threshold in whole currency units (USD). Alerts fire at 50/90/100% of actual spend and 100% of forecast."
  type        = number
  default     = 50
}

variable "enable_daily_sweep_scheduler" {
  description = "When true, Cloud Scheduler runs daily-sweep-report Mon–Fri at 9:00 AM Eastern. Enable only after the job secret is populated and a manual run succeeds."
  type        = bool
  default     = false
}

variable "github_repo" {
  description = "GitHub repository allowed to deploy keylessly via Workload Identity Federation, in owner/repo form."
  type        = string
  default     = "andrew-platformeq/tools-gcp"
}
