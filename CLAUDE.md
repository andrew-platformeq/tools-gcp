# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

`tools-gcp` — PlatformEq internal tools on non-prod GCP. A minimal,
GCP-ready **FastAPI** service plus the **Terraform** that bootstraps the project
it runs in. Python 3.11, `src/` layout, deployed to **Cloud Run**.

## Commands (use the Makefile, not raw tools)

| Command | What it does |
|---------|--------------|
| `make install` | Create `.venv` and install `-e ".[dev]"` |
| `make dev` | Run uvicorn locally on `:8080` (loads `.env`) |
| `make test` | `pytest` with `TOOLS_SKIP_GCP=1` |
| `make lint` | `ruff check src tests` |
| `make ci` | Full local CI: ruff + pip-audit + pytest (mirrors GitHub Actions) |
| `make verify` | `scripts/verify-setup.sh` — clone-to-running prerequisite checks |
| `make deploy` | Build via Cloud Build, deploy to Cloud Run (mutating — confirm first) |
| `make smoke` | Hit `/health` and `/ready` on the live Cloud Run URL |

- Tests require `TOOLS_SKIP_GCP=1` so they run without GCP credentials.
  `make test` sets it; if you run `pytest` directly, set it yourself.
- Lint config: ruff, line-length 100, target py3.11, rules `E,F,I,W` (see `pyproject.toml`).

## Layout

- `src/tools/` — the package
  - `config.py` — env-based settings, **non-secret only**, frozen dataclass
  - `secrets.py` — Secret Manager access (`get_secret`, `secret_is_accessible`)
  - `app.py` — FastAPI app + `tools-serve` entry point
- `tests/` — pytest
- `infra/terraform/` — project bootstrap (see below)
- `scripts/` — `bootstrap-project.sh`, `verify-setup.sh`, report generators
- `docs/` — `CLONE_TO_RUNNING.md`, `GCP_SETUP.md`, `GIT_STANDARDS.md`, `SECRETS.md`

Endpoints: `/health` (liveness, no GCP) and `/ready` (checks Secret Manager unless `skip_gcp`).

## GCP & config

- Project ID is **`peq-tools`** (region `us-central1`). Secret container:
  `peq-tools-app-config`. These are the live defaults in `config.py`.
- Settings come from `TOOLS_*` env vars: `TOOLS_GCP_PROJECT`,
  `TOOLS_GCP_REGION`, `TOOLS_SECRET_NAME`, `TOOLS_ENVIRONMENT`,
  `TOOLS_SKIP_GCP`.

### Authentication model (the most important design rule)

| Context | Mechanism |
|---------|-----------|
| Local dev | `gcloud auth application-default login` (ADC; creds in OS keychain) |
| Cloud Run | Attached runtime service account identity |
| GitHub CI | GCP intentionally skipped (`TOOLS_SKIP_GCP=1`); lint + unit tests only |

Local dev and Cloud Run talk to **real** `peq-tools` GCP. To connect locally
the first time: `gcloud auth application-default login` then
`gcloud config set project peq-tools` — after that `/ready` reaches Secret
Manager and returns `secret_configured: true`.

`TOOLS_SKIP_GCP=1` is a deliberate offline switch for **unit tests and
offline dev only** — not the normal mode. CI still uses it because keyless CI
auth (GitHub Workload Identity Federation) isn't wired up yet.

**Never create or commit a service-account key file.** No SA keys on disk.

## Secrets

- `.env` holds **non-secret config only** and is gitignored. Never put passwords,
  API keys, or tokens in `.env`, code, or Terraform state.
- Secret *values* live in Secret Manager (set via Console / `gcloud`). Terraform
  manages the secret *container*, not its values. See `docs/SECRETS.md`.

## Infrastructure (Terraform)

- `infra/terraform/` bootstraps the non-prod project: enables APIs, developer IAM
  bindings, GCS bucket, Secret Manager container, Cloud Run runtime SA, Artifact
  Registry repo, org policy, Cloud Build, and audit config.
- Terraform does **not** deploy the Cloud Run service — `make deploy` does.
- Remote state lives in **GCS** (`backend.hcl`). For local-only state use
  `local_backend_override.tf.example` (copy it) — do not edit the GCS backend
  to work around it.
- `bootstrap-project.sh` (run by an admin with billing + org permissions) creates
  the project itself, before Terraform runs.

## Git workflow

- Branch from latest `main`: `feature/<ticket>-<desc>`, `fix/...`, `chore/...`.
- **No direct pushes to `main`.** Open a PR, fill the template, one approving review,
  CI (`lint-and-test`) must pass. Squash-merge by default.
- Conventional Commits: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `infra`.
- Full rules: `docs/GIT_STANDARDS.md`. Run `make ci` before pushing.
