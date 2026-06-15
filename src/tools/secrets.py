"""Secret Manager access via Application Default Credentials — no keys on disk."""

from __future__ import annotations

import logging

from google.api_core import exceptions as gcp_exceptions
from google.cloud import secretmanager

from tools.config import Settings, get_settings

logger = logging.getLogger(__name__)


def get_secret(secret_name: str | None = None, *, settings: Settings | None = None) -> str:
    """Fetch the latest version of a secret from Secret Manager."""
    cfg = settings or get_settings()
    name = secret_name or cfg.secret_name
    resource = f"projects/{cfg.gcp_project}/secrets/{name}/versions/latest"

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": resource})
    return response.payload.data.decode("utf-8")


def secret_is_accessible(*, settings: Settings | None = None) -> bool:
    """Return True if the configured secret can be read (used by /ready)."""
    cfg = settings or get_settings()
    if cfg.skip_gcp:
        return True

    try:
        get_secret(settings=cfg)
        return True
    except gcp_exceptions.PermissionDenied:
        logger.warning("Secret Manager permission denied for %s", cfg.secret_name)
        return False
    except gcp_exceptions.NotFound:
        logger.warning("Secret not found: %s", cfg.secret_name)
        return False
    except Exception:
        logger.exception("Unexpected error accessing secret %s", cfg.secret_name)
        return False
