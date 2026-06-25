# EML Viewer telemetry (Phase B)

Public Cloud Run service that receives usage events from the Chrome extension
and lands them in BigQuery bronze. Gold views power adoption and reliability
dashboards.

Extension repo: `platformeq-eml-converter` (client flush + build-time URL).

## Architecture

```
Extension flush() → eml-viewer-telemetry (API key) → eml_viewer_bronze.events → eml_viewer_gold.*
```

Main `tools-gcp` service stays **private** (IAM). Only `eml-viewer-telemetry` allows
unauthenticated HTTPS; the app validates `Authorization: Bearer <api_key>`.

## Public access (org policy)

The Chrome extension sends a normal `fetch()` — it **cannot** use `gcloud auth`
or GCP identity tokens. Cloud Run must grant `roles/run.invoker` to **`allUsers`**
on `eml-viewer-telemetry` only.

If deploy warns `Setting IAM policy failed` or `bind-telemetry-public` errors with
*permitted customer*, your **organization policy** blocks public Cloud Run access
(typically `constraints/iam.allowedPolicyMemberDomains`).

**Until an org admin allows this binding**, the service may work for you via
identity token (`make smoke-telemetry` falls back to that) but **the extension
cannot flush**.

Ask your GCP org admin to either:

1. Allow `allUsers` as `roles/run.invoker` on `eml-viewer-telemetry` in `peq-tools`, or
2. Add a project-level exception for `peq-tools` under `iam.allowedPolicyMemberDomains`

Retry after approval:

```bash
make bind-telemetry-public
make smoke-telemetry    # should print "(public /health OK)" with no fallback message
```

## Bootstrap (first time)

**Order matters:** build and push the container image, then deploy the Cloud Run
service. Terraform owns BigQuery + Secret Manager only (not the service — same as
`tools-gcp`).

```bash
# 1. Terraform — BigQuery, secret container, IAM
cd infra/terraform
terraform state rm google_cloud_run_v2_service.eml_viewer_telemetry 2>/dev/null || true
terraform state rm google_cloud_run_v2_service_iam_member.eml_viewer_telemetry_public 2>/dev/null || true
terraform apply

# 2. Build image and deploy the public ingest service
cd ../..
make deploy                    # or: make deploy-telemetry-service if image already pushed
make apply-bq-eml-viewer       # gold views
echo -n '{"api_key":"dev-key-change-me"}' | \
  gcloud secrets versions add peq-tools-eml-viewer-telemetry-config --data-file=-

make smoke-telemetry
```

Copy the ingest URL from deploy output or:

```bash
gcloud run services describe eml-viewer-telemetry --region us-central1 --format='value(status.url)'
```

Full ingest path: `{url}/v1/eml-viewer/telemetry`

## Extension dev build

In `platformeq-eml-converter`, copy `.env.local.example` to `.env.local` and set
the URL + matching API key. Then:

```bash
npm run build
# Reload unpacked extension from dist/
```

## Verify ingest

```bash
curl -sf -X POST "$TELEMETRY_URL/v1/eml-viewer/telemetry" \
  -H "Authorization: Bearer dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"events":[{"event":"extension_opened","ts":"2026-06-23T12:00:00.000Z","user_email":"you@platformeq.com","identity_source":"chrome","install_id":"test","session_id":"test","extension_version":"0.1.0","chrome_version":"1.0","platform":"test","properties":{}}]}'
```

Query bronze:

```bash
bq query --use_legacy_sql=false \
  'SELECT event, user_email, ts FROM `peq-tools.eml_viewer_bronze.events` ORDER BY ingested_at DESC LIMIT 10'
```

## Gold views

| View | Purpose |
|------|---------|
| `gold_daily_active_users` | Distinct users/installs per day |
| `gold_import_success_rate` | Success vs fail vs rejected |
| `gold_repeat_file_opens` | Same fingerprint opened 2+ times |
| `gold_unique_files_vs_imports` | Distinct files vs total imports |

## Secret format

JSON object in `peq-tools-eml-viewer-telemetry-config`:

```json
{ "api_key": "your-key" }
```

Rotate by adding a new secret version and rebuilding the extension with the new
`VITE_TELEMETRY_API_KEY`.

## Deletion protection

Cloud Run **deletion protection** is an API/Terraform setting — `gcloud run deploy`
does not expose a `--deletion-protection` flag (as of gcloud SDK 571). Services
deployed via `make deploy` are not deletion-protected unless you add that separately.

If a service was ever created by Terraform with `deletion_protection = true`, you
must disable it before `gcloud` or Terraform can replace/delete the service:

```bash
gcloud run services update eml-viewer-telemetry --region us-central1 --no-deletion-protection
```

For Makefile-managed services, accidental delete risk is mitigated by IAM (only
project editors can delete) rather than the Cloud Run deletion_protection flag.
