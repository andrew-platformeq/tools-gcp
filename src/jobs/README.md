# Jobs

Each scheduled or CLI-run utility lives in its own folder under `src/jobs/`.

## Layout

```
src/jobs/
  daily-sweep-report/     # Linear sweep summary email (Mon–Fri)
  <future-job>/           # one folder per job — keep code isolated
```

Folder names use **kebab-case** (`daily-sweep-report`). Python imports use **snake_case**
(`daily_sweep_report`) via `package-dir` mapping in `pyproject.toml`.

## Conventions

| Concern | Where it lives |
|---------|----------------|
| Shared GCP helpers (ADC, base config) | `src/tools/` |
| Job-specific logic | `src/jobs/<job-name>/` |
| Job secrets (values) | Secret Manager — one secret container per job |
| Job CLI entry point | `[project.scripts]` in `pyproject.toml` as `tools-<job-name>` |
| Job tests | `tests/jobs/<job_name>/` |

## Adding a new job

1. Create `src/jobs/my-new-job/` with `main.py` and supporting modules.
2. Add package mapping in `pyproject.toml`:
   ```toml
   my_new_job = "src/jobs/my-new-job"
   ```
3. Add CLI: `tools-my-new-job = "my_new_job.main:main"`
4. Add a Secret Manager container in Terraform (if the job needs secrets).
5. Add tests under `tests/jobs/my_new_job/`.
6. Add a `make my-new-job` target (optional, for local runs).

## Running a job locally

```bash
gcloud auth application-default login
gcloud config set project peq-tools

# Dry run (no email sent)
TOOLS_SKIP_GCP=1 tools-daily-sweep-report --dry-run

# Live run (reads secrets from Secret Manager)
tools-daily-sweep-report
```

## Secret setup (daily-sweep-report)

Full technical guide: **[docs/daily-sweep-report-guide.pdf](../../docs/daily-sweep-report-guide.pdf)**  
Generate locally: `make docs-daily-sweep`

### Where this lives in GCP

All tools-gcp resources run in project **`peq-tools`** (separate from `peq-non-prod` / platformeq-gcp).

| Resource | Name | Purpose |
|----------|------|---------|
| **Secret Manager** | `peq-tools-daily-sweep-report-config` | This job's credentials only (JSON) |
| **Secret Manager** | `peq-tools-app-config` | Platform shell app (unrelated to this job) |
| **Service account** | `tools-gcp-run@peq-tools.iam.gserviceaccount.com` | Runtime identity (reads secrets, no key file) |
| **Artifact Registry** | `us-central1-docker.pkg.dev/peq-tools/tools-gcp` | Shared Docker image for app + jobs |
| **Region** | `us-central1` | Cloud Run / AR default |

**Isolation model:** one Secret Manager **container per job** (`peq-tools-<job-name>-config`), with IAM scoped so the runtime SA can read only the secrets Terraform grants. Future jobs get their own folder, secret, and (later) Cloud Run Job — not shared GitHub Secrets or a single `.env`.

Console link (after apply):  
https://console.cloud.google.com/security/secret-manager?project=peq-tools

Add credentials as JSON after `terraform apply` (values never in git):

```bash
cat <<'EOF' | gcloud secrets versions add peq-tools-daily-sweep-report-config --data-file=-
{
  "gmail_address": "your-bot@gmail.com",
  "gmail_app_password": "your-gmail-app-password",
  "send_to": "team@platformeq.com",
  "linear_api_key": "lin_api_..."
}
EOF
```

For local testing without Secret Manager, use `TOOLS_SKIP_GCP=1 tools-daily-sweep-report --dry-run`.
