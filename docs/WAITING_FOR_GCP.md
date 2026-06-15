# Waiting for GCP — Pre-Bootstrap Checklist

Use this while the empty `tools-non-prod` project is being created.

## What Joe needs to do (one time)

1. Create project `tools-non-prod`
2. Link billing to that project
3. Grant you **Editor**: `user:andrew@platformeq.com`

See [GCP_SETUP.md](./GCP_SETUP.md) for the exact commands.

## What you can do now (no GCP required)

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project tools-non-prod

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
gcloud projects describe tools-non-prod
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
