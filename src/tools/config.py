"""Application configuration from environment variables (non-secret only)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    gcp_project: str
    gcp_region: str
    secret_name: str
    environment: str
    skip_gcp: bool

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            gcp_project=os.environ.get("TOOLS_GCP_PROJECT", "peq-tools"),
            gcp_region=os.environ.get("TOOLS_GCP_REGION", "us-central1"),
            secret_name=os.environ.get(
                "TOOLS_SECRET_NAME", "peq-tools-app-config"
            ),
            environment=os.environ.get("TOOLS_ENVIRONMENT", "nonprod"),
            skip_gcp=os.environ.get("TOOLS_SKIP_GCP", "").lower() in ("1", "true", "yes"),
        )


def get_settings() -> Settings:
    return Settings.from_env()
