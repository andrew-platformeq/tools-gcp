# GCP Non-Prod Setup

Bootstrap guide for the **non-prod** GCP project. Production is out of scope.

## Target State

| Resource | Purpose |
|----------|---------|
| GCP project `peq-tools` | Isolated non-prod boundary |
| Enabled APIs | Run, Secret Manager, GCS, BigQuery, Artifact Registry, Cloud Build, Org Policy |
| IAM for developers | Resource-scoped roles on bucket, secret, registry, Cloud Run SA |
| GCS dev sandbox bucket | Dev artifact / data scratch space (`force_destroy` enabled) |
| GCS Terraform state bucket | Shared remote state, versioned, no `force_destroy` |
| Secret Manager secret | App config container (value added via `gcloud`, not Terraform) |
| Cloud Run service account | Runtime identity (no key file) |
| Audit logging | Secret Manager `DATA_READ` enabled |
| Org policies (optional) | Block SA key creation/upload when project is under an org |

Okta-to-GCP federation is **Phase 2** — user IAM binding via Google account is sufficient for Phase 1.

## Prerequisites (Org Admin — Joe)

- Billing account linked
- Permission to create projects or assign an existing project
- Terraform ≥ 1.5

## Step 1 — Create the Project

Week-1 critical path if the project does not exist:

```bash
export PROJECT_ID=peq-tools
export BILLING_ACCOUNT=<billing-account-id>
export REGION=us-central1

gcloud projects create "$PROJECT_ID" --name="Tools Non-Prod"
gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"
```

Or use the bootstrap script:

```bash
export BILLING_ACCOUNT=<billing-id>
export MEMBER="user:andrew@example.com"
./scripts/bootstrap-project.sh
```

## Step 2 — Apply Terraform

Terraform uses a **two-step state bootstrap**: the state bucket is created by Terraform itself, so the first apply uses local state, then you migrate to GCS.

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: set project_id, developers (Google emails as user:...)
# Set enforce_no_sa_keys = true if the project is under a GCP organization

# First apply — local state (state bucket does not exist yet)
cp local_backend_override.tf.example local_backend_override.tf
terraform init -reconfigure
terraform plan
terraform apply

# Migrate to remote state in GCS
rm local_backend_override.tf
cp backend.hcl.example backend.hcl
# Edit backend.hcl: bucket = "<project_id>-terraform-state"
terraform init -backend-config=backend.hcl -migrate-state

# Add the first secret version (Terraform creates the container only)
echo -n "dev-placeholder-rotate-me" | gcloud secrets versions add "${PROJECT_ID}-app-config" --data-file=-
```

Subsequent applies:

```bash
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

Terraform enables APIs, binds IAM, creates buckets, the secret container, Cloud Run SA, Artifact Registry repo, audit config, and optional org policies.

## Developer IAM Roles

| Role | ID | Scope |
|------|----|-------|
| BigQuery User | `roles/bigquery.user` | Project (until datasets are in Terraform) |
| Cloud Run Developer | `roles/run.developer` | Project |
| Storage Object Admin | `roles/storage.objectAdmin` | Dev sandbox + Terraform state buckets only |
| Secret Manager Secret Accessor | `roles/secretmanager.secretAccessor` | `app-config` secret only |
| Artifact Registry Writer | `roles/artifactregistry.writer` | App registry repo only |
| Cloud Build Editor | `roles/cloudbuild.builds.editor` | Project |
| Service Account User | `roles/iam.serviceAccountUser` | Cloud Run runtime SA only |

Additional developers: add their `user:email@domain` to the `developers` list in `terraform.tfvars` and run `terraform apply`.

## Zero Admin Keys

Org policies are enforced in Terraform when `enforce_no_sa_keys = true` (requires project under a GCP organization):

- `iam.disableServiceAccountKeyCreation`
- `iam.disableServiceAccountKeyUpload`

Manual checklist if no org is available:

- [ ] No `gcloud iam service-accounts keys create` in docs or scripts
- [ ] Audit: `gcloud iam service-accounts keys list --iam-account=SA_EMAIL` returns empty
- [ ] Cloud Run uses attached SA only — never a downloaded key

Verify no keys exist:

```bash
for sa in $(gcloud iam service-accounts list --format='value(email)'); do
  echo "=== $sa ==="
  gcloud iam service-accounts keys list --iam-account="$sa"
done
```

## Step 3 — First Deploy

After a developer completes [CLONE_TO_RUNNING.md](./CLONE_TO_RUNNING.md):

```bash
make deploy
make smoke
```

Cloud Run is deployed **authenticated** (`--no-allow-unauthenticated`). `make smoke` uses your `gcloud` identity token — you must have `roles/run.invoker` (included in `run.developer`).

## Rollback

```bash
cd infra/terraform
terraform destroy   # tears down resources; does NOT delete the project
```

To remove the project entirely (admin only):

```bash
gcloud projects delete peq-tools
```

## Scope Boundary

This repo covers the **dev / cloud layer** only. Generic SaaS onboarding (email, Slack, Linear, Notion) is handled separately by Thia + Leo. The healthcare pipeline (Dataproc, Composer, medallion layers) runs on this platform later — it is not in scope for Phase 1.
