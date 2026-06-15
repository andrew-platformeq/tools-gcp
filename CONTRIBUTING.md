# Contributing

Thank you for contributing to `tools-gcp`. Read this before opening a PR.

## Quick Links

- [Git standards (branching, commits, review)](docs/GIT_STANDARDS.md)
- [Secrets policy — no keys on disk](docs/SECRETS.md)
- [Clone-to-running checklist](docs/CLONE_TO_RUNNING.md)
- [GCP non-prod setup (admin)](docs/GCP_SETUP.md)

## Workflow

1. Branch from `main`: `feature/<ticket>-<desc>` or `fix/<ticket>-<desc>`
2. Make changes; run `make lint` and `make test` locally
3. Run `./scripts/verify-setup.sh` to confirm no secrets on disk
4. Push and open a PR against `main`
5. Get one approval; CI (`lint-and-test`) must pass

## Commit Format

```
<type>(<scope>): <imperative summary>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `infra`.

## Secrets

- Never commit `.env` files with real values
- Never commit service account JSON keys
- Use `gcloud auth application-default login` locally
- Store secret values in Secret Manager only

## Questions

- SaaS onboarding (Slack, Linear, etc.): ask Thia
- GCP org / billing: ask Joe
- This repo / dev environment: open a GitHub issue
