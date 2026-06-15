locals {
  apis = [
    # Core platform (Phase 1)
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "orgpolicy.googleapis.com",

    # Observability & financial guardrails (Phase 2, Tier-1)
    "logging.googleapis.com",              # Cloud Run/Build stdout + structured logs
    "monitoring.googleapis.com",           # metrics, alert policies, notification channels
    "cloudresourcemanager.googleapis.com", # project metadata; underpins asset/policy tooling
    "recommender.googleapis.com",          # Active Assist: IAM-too-broad + cost recommendations
    "cloudasset.googleapis.com",           # queryable inventory of buckets/secrets/datasets
    "billingbudgets.googleapis.com",       # Terraform-managed budget + threshold alerts

    # Keyless CI — Workload Identity Federation (Phase 2, Pillar 3)
    "iamcredentials.googleapis.com", # mint short-lived tokens for the deployer SA
    "sts.googleapis.com",            # OIDC token exchange (GitHub -> GCP)
  ]

  # Intentionally omitted:
  #   maintenance.googleapis.com — only useful with VMs/persistent DBs; you're serverless.
  #     Add it alongside the first Cloud SQL / persistent datastore, not before.
  #   appoptimize.googleapis.com — not a standard Service Usage API name; enabling it would
  #     fail `terraform apply`. The cost-summary widget it referred to is the billing console's
  #     FinOps view, powered by billing export + recommender.googleapis.com (already enabled).
}

resource "google_project_service" "apis" {
  for_each = toset(local.apis)

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
