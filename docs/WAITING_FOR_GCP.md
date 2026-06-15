# Waiting for GCP — Pre-Bootstrap Checklist

Use this while Terraform has not yet been applied to `peq-tools`.

## Project status

The GCP project **`peq-tools`** already exists. Remaining bootstrap steps:

1. Confirm billing is linked to `peq-tools`
2. Apply Terraform (see [GCP_SETUP.md](./GCP_SETUP.md))
3. Add the first secret version and deploy

## What you can do now

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project peq-tools

make install
cp .env.example .env
make ci
make verify
```

Prepare Terraform config (do not apply until the project exists):

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit: project_id, member = user:andrew@platformeq.com
```

## When Joe says the project is ready

```bash
# Confirm access
gcloud projects describe peq-tools
make verify

# Bootstrap infrastructure (manual — see GCP_SETUP.md Step 2)
cd infra/terraform
terraform init -reconfigure
terraform plan
terraform apply
# then migrate state and add secret version per GCP_SETUP.md

# First deploy
make deploy
make smoke
```

Done when [CLONE_TO_RUNNING.md](./CLONE_TO_RUNNING.md) checklist passes.

## Optional before bootstrap

- Enable **branch protection** on `main` (require `lint-and-test` CI)
- Set a **billing budget alert** in GCP Console ($10–25/month)
