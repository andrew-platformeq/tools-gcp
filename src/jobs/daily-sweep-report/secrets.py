"""Load job credentials from Secret Manager (JSON secret)."""

from __future__ import annotations

import json

from daily_sweep_report.config import JobSettings, ReportSecrets

from tools.secrets import get_secret


def load_report_secrets(settings: JobSettings | None = None) -> ReportSecrets:
    """Fetch and parse the daily-sweep-report secret from Secret Manager."""
    cfg = settings or JobSettings.from_env()
    if cfg.skip_gcp:
        return ReportSecrets(
            gmail_address="dry-run@example.com",
            gmail_app_password="unused",
            send_to="dry-run@example.com",
            linear_api_key="dry-run-key",
        )

    raw = get_secret(cfg.secret_name)
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "Daily sweep report secret must be a JSON object"
        raise TypeError(msg)
    return ReportSecrets.from_mapping({str(k): str(v) for k, v in data.items()})
