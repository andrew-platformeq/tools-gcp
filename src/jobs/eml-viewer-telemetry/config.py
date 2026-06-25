"""Non-secret configuration for the eml-viewer-telemetry service."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_SECRET_NAME = "peq-tools-eml-viewer-telemetry-config"
DEFAULT_BRONZE_DATASET = "eml_viewer_bronze"
DEFAULT_BRONZE_TABLE = "events"


@dataclass(frozen=True)
class Settings:
    gcp_project: str
    gcp_region: str
    secret_name: str
    bronze_dataset: str
    bronze_table: str
    environment: str
    skip_gcp: bool
    test_api_key: str | None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            gcp_project=os.environ.get("TOOLS_GCP_PROJECT", "peq-tools"),
            gcp_region=os.environ.get("TOOLS_GCP_REGION", "us-central1"),
            secret_name=os.environ.get(
                "TOOLS_EML_VIEWER_TELEMETRY_SECRET_NAME",
                DEFAULT_SECRET_NAME,
            ),
            bronze_dataset=os.environ.get(
                "TOOLS_EML_VIEWER_BRONZE_DATASET",
                DEFAULT_BRONZE_DATASET,
            ),
            bronze_table=os.environ.get(
                "TOOLS_EML_VIEWER_BRONZE_TABLE",
                DEFAULT_BRONZE_TABLE,
            ),
            environment=os.environ.get("TOOLS_ENVIRONMENT", "nonprod"),
            skip_gcp=os.environ.get("TOOLS_SKIP_GCP", "").lower() in ("1", "true", "yes"),
            test_api_key=os.environ.get("TOOLS_EML_VIEWER_TELEMETRY_TEST_API_KEY"),
        )

    @property
    def bronze_table_id(self) -> str:
        return f"{self.gcp_project}.{self.bronze_dataset}.{self.bronze_table}"


@dataclass(frozen=True)
class TelemetrySecrets:
    api_key: str

    @classmethod
    def from_mapping(cls, data: dict[str, str]) -> TelemetrySecrets:
        key = data.get("api_key", "").strip()
        if not key:
            msg = "eml-viewer-telemetry secret must include api_key"
            raise ValueError(msg)
        return cls(api_key=key)


def get_settings() -> Settings:
    return Settings.from_env()
