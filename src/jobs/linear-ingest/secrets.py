"""Load linear-ingest credentials from Secret Manager."""

from __future__ import annotations

import json

from linear_ingest.config import IngestSecrets, JobSettings

from tools.secrets import get_secret


def load_ingest_secrets(settings: JobSettings | None = None) -> IngestSecrets:
    """Fetch and parse the linear-ingest secret from Secret Manager."""
    cfg = settings or JobSettings.from_env()
    if cfg.skip_gcp:
        return IngestSecrets(linear_api_key="dry-run-key")

    raw = get_secret(cfg.secret_name)
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "Linear ingest secret must be a JSON object"
        raise TypeError(msg)
    return IngestSecrets.from_mapping({str(k): str(v) for k, v in data.items()})
