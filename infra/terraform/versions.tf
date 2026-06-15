terraform {
  required_version = ">= 1.5"

  # Remote state — configure via backend.hcl after the state bucket exists.
  # First bootstrap: terraform init -backend=false, apply, then migrate — see GCP_SETUP.md.
  backend "gcs" {}

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region

  # Some APIs (e.g. billingbudgets) require a quota/billing project when
  # authenticating with user ADC. Attribute those calls to this project so they
  # don't fall back to a default project where the API isn't enabled.
  billing_project       = var.project_id
  user_project_override = true
}
