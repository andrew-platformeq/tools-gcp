"""Load eml-viewer-telemetry credentials from Secret Manager."""

from __future__ import annotations

import json

from eml_viewer_telemetry.config import Settings, TelemetrySecrets, get_settings

from tools.secrets import get_secret


def load_telemetry_secrets(settings: Settings | None = None) -> TelemetrySecrets:
    """Fetch and parse the telemetry ingest secret from Secret Manager."""
    cfg = settings or get_settings()
    if cfg.skip_gcp:
        key = cfg.test_api_key or "test-telemetry-key"
        return TelemetrySecrets(api_key=key)

    raw = get_secret(cfg.secret_name)
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "eml-viewer-telemetry secret must be a JSON object"
        raise TypeError(msg)
    return TelemetrySecrets.from_mapping({str(k): str(v) for k, v in data.items()})
