# tools-gcp

Non-prod GCP platform for PlatformEq internal tools — where code lives and runs.

**Done means:** a fresh checkout builds and runs in non-prod with no secrets on disk.

This repo mirrors the [platformeq-gcp](https://github.com/andrew-platformeq/platformeq-gcp) infrastructure pattern: a minimal FastAPI service on Cloud Run with Secret Manager, Terraform bootstrap, and keyless CI deploy via Workload Identity Federation.

## Quick Start

```bash
git clone https://github.com/andrew-platformeq/tools-gcp.git
cd tools-gcp

gcloud auth login
gcloud auth application-default login
gcloud config set project peq-tools

make install
cp .env.example .env
make dev
```

Full acceptance checklist: **[docs/CLONE_TO_RUNNING.md](docs/CLONE_TO_RUNNING.md)**

Waiting for the GCP project? See **[docs/WAITING_FOR_GCP.md](docs/WAITING_FOR_GCP.md)**

## Repository Layout

```
├── src/tools/              Shared platform code (config, secrets, FastAPI app)
├── src/jobs/               Scheduled jobs and utilities (one folder per job)
│   └── daily-sweep-report/ Daily Linear sweep summary email
├── tests/                  Unit tests (no GCP credentials required)
├── infra/terraform/        Non-prod GCP project IAM and resources
├── scripts/                Bootstrap and verification scripts
├── docs/                   Standards and setup guides
└── .github/workflows/      CI (lint + test)
```

## Make Targets

| Target | Description |
|--------|-------------|
| `make install` | Create venv, install deps |
| `make dev` | Run local server on `:8080` |
| `make test` | Run pytest (GCP mocked) |
| `make lint` | Run ruff |
| `make ci` | Full CI suite locally (lint + pip-audit + test) |
| `make verify` | Clone-to-running prerequisite checks |
| `make deploy` | Build and deploy to Cloud Run |
| `make smoke` | Hit deployed `/health` and `/ready` |

## Standards

| Topic | Document |
|-------|----------|
| Git / PR / commits | [docs/GIT_STANDARDS.md](docs/GIT_STANDARDS.md) |
| Secrets (no keys on disk) | [docs/SECRETS.md](docs/SECRETS.md) |
| GCP non-prod bootstrap | [docs/GCP_SETUP.md](docs/GCP_SETUP.md) |
| Daily sweep report job | [docs/daily-sweep-report-guide.pdf](docs/daily-sweep-report-guide.pdf) |
| Setup walkthrough (PDF) | [docs/tools-gcp-setup-walkthrough.pdf](docs/tools-gcp-setup-walkthrough.pdf) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Scope and Limits

- **Non-prod only** — no production, no regulated data, no EPIC
- **Secrets:** `gcloud auth` + Secret Manager; no service account keys on disk
- **Phase 2:** Okta → GCP federation, GitHub WIF for CI deploy
- **SaaS onboarding** (email, Slack, Linear): handled separately — this is the dev/cloud layer

## Admin Bootstrap (Week 1 Critical Path)

The non-prod GCP project must exist before developers can complete clone-to-running. Ask Joe:

```bash
export BILLING_ACCOUNT=<billing-id>
export MEMBER="user:andrew@example.com"
./scripts/bootstrap-project.sh
```

## CI

GitHub Actions runs `lint-and-test` (ruff + pip-audit + pytest) on every push/PR to `main`. No GCP credentials in CI. Run `make ci` locally to match.

Branch protection on `main` should require the `lint-and-test` check — see [docs/GIT_STANDARDS.md](docs/GIT_STANDARDS.md).
