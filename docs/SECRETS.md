# Secrets Policy

Non-negotiable from day 1: **no secrets on disk, no service account keys in git.**

## How Authentication Works

```
Developer laptop                GCP (non-prod)
─────────────────              ─────────────────
gcloud auth login        →     User identity
gcloud auth application-default login  →  ADC for SDKs
                                 │
                                 ├─ Secret Manager (read secrets)
                                 ├─ Cloud Run (deploy)
                                 ├─ GCS (read/write objects)
                                 └─ BigQuery (query jobs)
```

Cloud Run workloads use an **attached service account** — never a downloaded key file.

## Local Development Setup

```bash
# One-time per machine
gcloud auth login
gcloud auth application-default login
gcloud config set project tools-non-prod
```

Verify:

```bash
gcloud auth list
gcloud auth application-default print-access-token > /dev/null && echo "ADC OK"
```

## Reading Secrets at Runtime

Application code uses Secret Manager via ADC:

```python
from tools.secrets import get_secret

value = get_secret("tools-non-prod-app-config")
```

Secret **names** are in code and docs. Secret **values** are set only in GCP Console or `gcloud secrets versions add`.

## Creating / Updating a Secret (Admin / Bootstrap)

Terraform creates the **secret container** only (no value in Terraform state). Add the first version after apply:

```bash
echo -n "dev-placeholder-rotate-me" | gcloud secrets versions add tools-non-prod-app-config --data-file=-

# Rotate later
echo -n "new-value" | gcloud secrets versions add tools-non-prod-app-config --data-file=-
```

See [GCP_SETUP.md](./GCP_SETUP.md) for the full bootstrap flow.

## Forbidden

| Action | Why |
|--------|-----|
| Commit `.env` with real values | Leaks credentials via git history |
| Download SA key JSON | Key persists on disk; hard to rotate |
| Put secrets in Dockerfile / Cloud Run env vars as plaintext | Visible in console and revision history |
| Share secrets via Slack/email | Unaudited, unrotatable |
| Run `gcloud iam service-accounts keys create` | Creates keys on disk |
| Store secret values in Terraform | Plaintext in remote/local state |

## Allowed Environment Variables

Only **non-secret** configuration belongs in env vars:

| Variable | Example | Secret? |
|----------|---------|---------|
| `TOOLS_GCP_PROJECT` | `tools-non-prod` | No |
| `TOOLS_GCP_REGION` | `us-central1` | No |
| `TOOLS_SECRET_NAME` | `tools-non-prod-app-config` | No (name only) |
| `PORT` | `8080` | No |

See `.env.example` for the full list.

## Audit Trail

- Secret **reads** are logged via Cloud Audit Logs (`DATA_READ` enabled for `secretmanager.googleapis.com` in Terraform).
- Secret admin operations (create, IAM changes) are logged by default.
- IAM changes are logged under `SetIamPolicy`.
- If secrets appear in git history, rotate immediately and use `git filter-repo` under admin supervision.

## CI / CD Authentication (Future)

Current CI is lint and test only — no GCP credentials needed.

When GitHub Actions deploys to Cloud Run or pushes images, use **Workload Identity Federation** (keyless):

- Create a workload identity pool + provider for GitHub OIDC
- Grant the federated principal only the roles it needs (Artifact Registry writer, Cloud Run developer, SA user on the runtime SA)
- Use [`google-github-actions/auth`](https://github.com/google-github-actions/auth) in the workflow

**Do not** store a service account key JSON in GitHub Secrets — that contradicts this policy.
