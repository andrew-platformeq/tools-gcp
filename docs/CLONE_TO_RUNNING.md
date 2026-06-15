# Clone-to-Running Checklist

Acceptance test: a fresh checkout builds and runs in non-prod with **no secrets on disk**.

## Prerequisites

- [ ] macOS or Linux (Windows via WSL2)
- [ ] Python 3.11+
- [ ] [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [ ] Access to GCP project `peq-tools` (scoped IAM)
- [ ] GitHub access to `andrew-platformeq/tools-gcp`

## Checklist

### 1. Clone

```bash
git clone https://github.com/andrew-platformeq/tools-gcp.git
cd tools-gcp
```

### 2. Authenticate (no keys on disk)

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project peq-tools
```

Verify no credential files in the repo:

```bash
./scripts/verify-setup.sh
```

Expected: all checks pass (GCP project must exist for `/ready` locally).

### 3. Install dependencies

```bash
make install
```

Creates `.venv/` (gitignored) and installs the package in editable mode.

### 4. Configure environment (non-secret values only)

```bash
cp .env.example .env
# .env contains only project ID and region — no secrets
```

### 5. Run locally

```bash
make dev
```

In another terminal:

```bash
curl -s http://localhost:8080/health | python -m json.tool
curl -s http://localhost:8080/ready | python -m json.tool
```

Expected `/health`:

```json
{
  "status": "ok",
  "project": "peq-tools",
  "environment": "nonprod"
}
```

Expected `/ready` (requires Secret Manager access and bootstrap secret):

```json
{
  "status": "ready",
  "secret_configured": true
}
```

### 6. Run tests

```bash
make test && make lint
```

### 7. Deploy to Cloud Run

```bash
make deploy
make smoke
```

Expected: HTTP 200 from the Cloud Run URL printed by `make deploy`.

### 8. Confirm no secret files created

```bash
find . -path './.venv' -prune -o \( -name '*credentials*' -o -name '*service-account*' -o -name 'adc.json' \) -print
```

Expected: no output.

## Done Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| a | Git standards live | [GIT_STANDARDS.md](./GIT_STANDARDS.md), `.github/workflows/ci.yml` |
| b | Non-prod GCP + scoped IAM | [GCP_SETUP.md](./GCP_SETUP.md), `infra/terraform/` |
| c | Dev sandboxes wired | GCS bucket, Secret Manager dummy, `Makefile` |
| ✓ | No secrets on disk | `verify-setup.sh`, `.gitignore`, [SECRETS.md](./SECRETS.md) |
| ✓ | Clone → running | Independent dev completes this checklist |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `403 Secret Manager` | Confirm IAM: `roles/secretmanager.secretAccessor` on your user |
| `Could not automatically determine credentials` | Run `gcloud auth application-default login` |
| `Project not found` | Ask Joe to confirm project exists and you are IAM-bound |
| `/ready` shows `secret_configured: false` | Run Terraform bootstrap or create secret per [GCP_SETUP.md](./GCP_SETUP.md) |
| Deploy fails on Cloud Build | Confirm AR + Cloud Build + SA User roles in Terraform |

## Phase 2 (not required for this checklist)

- GitHub Workload Identity Federation for keyless CI deploy
- Okta → GCP workforce federation
- Auto-deploy on merge to `main`

<--cask Leo verified local dev + PR pipeline 2026-06-15 -->
