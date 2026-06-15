# Remote Terraform state bucket — shared, versioned, no force_destroy.
# Bootstrap: first apply uses local state (-backend=false), then migrate — see GCP_SETUP.md.

resource "google_storage_bucket" "terraform_state" {
  name          = "${var.project_id}-terraform-state"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    purpose     = "terraform-state"
  }

  depends_on = [google_project_service.apis]
}
