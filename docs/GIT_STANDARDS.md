# Git Standards

Auditable conventions for the `tools-gcp` repository.

## Branching

| Branch | Purpose |
|--------|---------|
| `main` | Protected default; always deployable to non-prod |
| `feature/<ticket>-<short-desc>` | New work |
| `fix/<ticket>-<short-desc>` | Bug fixes |
| `chore/<short-desc>` | Tooling, docs, infra-only changes |

Rules:

- Branch from latest `main`.
- Keep branches short-lived (target ≤ 3 days).
- Rebase or merge `main` before opening a PR if your branch is stale.

## Pull Requests

1. Open a PR against `main` — no direct pushes to `main`.
2. Fill in the PR template (summary, test plan, secrets check).
3. Require **one approving review** before merge.
4. CI must pass (`lint-and-test` job).
5. Squash-merge unless a multi-commit history is intentionally needed.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <imperative summary>

[optional body]

[optional footer: Fixes #123]
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `infra`.

Examples:

```
feat(run): add health check endpoint for Cloud Run
infra(iam): grant developer secretmanager.secretAccessor on non-prod
docs: document clone-to-running checklist
```

## Secrets and `.env` Handling

**Never commit secrets.** Enforced by `.gitignore` and review.

| Allowed on disk | Forbidden on disk |
|-----------------|-------------------|
| `.env.example` (names only, no values) | `.env`, `.env.local`, `.env.*.local` |
| `gcloud` user credentials via `gcloud auth` | Service account JSON keys |
| Application Default Credentials (ADC) in OS keychain | `adc.json`, credential JSON files |
| Secret Manager references (secret *names*, not values) | API tokens, passwords, private keys |

See [SECRETS.md](./SECRETS.md) for the full policy.

## CI

GitHub Actions runs on every push and PR to `main`:

- `ruff check` — lint
- `pytest` — unit tests (GCP calls mocked; no cloud credentials in CI)

Deploy workflows are added in Phase 2 once Workload Identity Federation is configured.

## Branch Protection (GitHub Admin)

Configure on `main` in GitHub → Settings → Branches:

- [ ] Require pull request before merging
- [ ] Require 1 approving review
- [ ] Require status check: **`lint-and-test`**
- [ ] Do not allow bypassing (including admins, if org policy permits)

## Code Review Checklist

Reviewers confirm:

- [ ] No secrets, keys, or `.env` files in the diff
- [ ] IAM changes follow least privilege
- [ ] New env vars documented in `.env.example`
- [ ] Tests cover non-trivial logic
- [ ] Infra changes have a rollback note in the PR body
