"""Non-secret configuration for the linear-ingest job."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_SECRET_NAME = "peq-tools-linear-ingest-config"
DEFAULT_BUCKET = "peq-tools-linear-data"
DEFAULT_WATERMARKS_BLOB = "state/watermarks.json"


@dataclass(frozen=True)
class JobSettings:
    gcp_project: str
    gcs_bucket: str
    watermarks_blob: str
    secret_name: str
    skip_gcp: bool
    dry_run: bool

    @classmethod
    def from_env(cls) -> JobSettings:
        project = os.environ.get("TOOLS_GCP_PROJECT", "peq-tools")
        return cls(
            gcp_project=project,
            gcs_bucket=os.environ.get("TOOLS_LINEAR_DATA_BUCKET", DEFAULT_BUCKET),
            watermarks_blob=os.environ.get(
                "TOOLS_LINEAR_WATERMARKS_BLOB",
                DEFAULT_WATERMARKS_BLOB,
            ),
            secret_name=os.environ.get(
                "TOOLS_LINEAR_INGEST_SECRET_NAME",
                DEFAULT_SECRET_NAME,
            ),
            skip_gcp=os.environ.get("TOOLS_SKIP_GCP", "").lower() in ("1", "true", "yes"),
            dry_run=os.environ.get("TOOLS_LINEAR_INGEST_DRY_RUN", "").lower()
            in ("1", "true", "yes"),
        )


@dataclass(frozen=True)
class IngestSecrets:
    linear_api_key: str

    @classmethod
    def from_mapping(cls, data: dict[str, str]) -> IngestSecrets:
        key = data.get("linear_api_key", "")
        if not key:
            msg = "Secret JSON missing required key: linear_api_key"
            raise ValueError(msg)
        return cls(linear_api_key=key)
