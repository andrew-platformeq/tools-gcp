# Block service account key creation/upload when the project sits under a GCP organization.
# Set enforce_no_sa_keys = false in terraform.tfvars if the project has no org (standalone).

resource "google_project_organization_policy" "disable_sa_key_creation" {
  count = var.enforce_no_sa_keys ? 1 : 0

  project    = var.project_id
  constraint = "iam.disableServiceAccountKeyCreation"

  boolean_policy {
    enforced = true
  }
}

resource "google_project_organization_policy" "disable_sa_key_upload" {
  count = var.enforce_no_sa_keys ? 1 : 0

  project    = var.project_id
  constraint = "iam.disableServiceAccountKeyUpload"

  boolean_policy {
    enforced = true
  }
}
