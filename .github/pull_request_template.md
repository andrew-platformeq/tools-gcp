## Summary

<!-- What changed and why? -->

## Test plan

- [ ] `make ci` (or `make lint` + `make test`)
- [ ] `./scripts/verify-setup.sh` (if touching auth/secrets/local dev)
- [ ] Manual verification steps:

## Secrets check

- [ ] No `.env`, credential JSON, or API keys in this PR
- [ ] New secret **names** (not values) documented in `.env.example` if applicable
- [ ] IAM changes follow least privilege

## Infra rollback (if applicable)

<!-- How to revert Terraform or deploy changes -->
