"""GCS-backed watermark state and bronze page storage."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Protocol

from linear_ingest.config import JobSettings
from linear_ingest.entities import WATERMARKS_VERSION

BRONZE_PREFIX = "bronze"


class BronzeStore(Protocol):
    def load_watermarks(self) -> dict[str, Any]: ...

    def save_watermarks(self, data: dict[str, Any]) -> None: ...

    def write_bronze_page(
        self,
        *,
        run_prefix: str,
        entity: str,
        page: int,
        payload: dict[str, Any],
    ) -> str: ...

    def write_summary(self, run_prefix: str, summary: dict[str, Any]) -> str: ...


class LocalBronzeStore:
    """Filesystem store for TOOLS_SKIP_GCP=1 local runs and unit tests."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(tempfile.gettempdir()) / "linear-ingest-local"
        self.watermarks_path = self.root / "state" / "watermarks.json"

    def load_watermarks(self) -> dict[str, Any]:
        if not self.watermarks_path.exists():
            return {"version": WATERMARKS_VERSION, "entities": {}}
        data = json.loads(self.watermarks_path.read_text(encoding="utf-8"))
        if "entities" not in data:
            msg = f"invalid watermarks file: {self.watermarks_path}"
            raise ValueError(msg)
        return data

    def save_watermarks(self, data: dict[str, Any]) -> None:
        self.watermarks_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.watermarks_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.watermarks_path)

    def write_bronze_page(
        self,
        *,
        run_prefix: str,
        entity: str,
        page: int,
        payload: dict[str, Any],
    ) -> str:
        path = self.root / run_prefix / entity / f"page_{page:04d}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return str(path)

    def write_summary(self, run_prefix: str, summary: dict[str, Any]) -> str:
        path = self.root / run_prefix / "summary.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        return str(path)


class GcsBronzeStore:
    """Production bronze + watermark storage in GCS."""

    def __init__(self, bucket_name: str, watermarks_blob: str, project: str) -> None:
        from google.cloud import storage

        self._client = storage.Client(project=project)
        self._bucket = self._client.bucket(bucket_name)
        self._watermarks_blob = watermarks_blob

    def load_watermarks(self) -> dict[str, Any]:
        blob = self._bucket.blob(self._watermarks_blob)
        if not blob.exists():
            return {"version": WATERMARKS_VERSION, "entities": {}}
        data = json.loads(blob.download_as_text(encoding="utf-8"))
        if "entities" not in data:
            msg = f"invalid watermarks blob: gs://{self._bucket.name}/{self._watermarks_blob}"
            raise ValueError(msg)
        return data

    def save_watermarks(self, data: dict[str, Any]) -> None:
        blob = self._bucket.blob(self._watermarks_blob)
        blob.upload_from_string(
            json.dumps(data, indent=2) + "\n",
            content_type="application/json",
        )

    def write_bronze_page(
        self,
        *,
        run_prefix: str,
        entity: str,
        page: int,
        payload: dict[str, Any],
    ) -> str:
        blob_name = f"{BRONZE_PREFIX}/{run_prefix}/{entity}/page_{page:04d}.json"
        blob = self._bucket.blob(blob_name)
        blob.upload_from_string(
            json.dumps(payload, indent=2) + "\n",
            content_type="application/json",
        )
        return f"gs://{self._bucket.name}/{blob_name}"

    def write_summary(self, run_prefix: str, summary: dict[str, Any]) -> str:
        blob_name = f"{BRONZE_PREFIX}/{run_prefix}/summary.json"
        blob = self._bucket.blob(blob_name)
        blob.upload_from_string(
            json.dumps(summary, indent=2) + "\n",
            content_type="application/json",
        )
        return f"gs://{self._bucket.name}/{blob_name}"


def get_bronze_store(settings: JobSettings) -> BronzeStore:
    if settings.skip_gcp:
        return LocalBronzeStore()
    return GcsBronzeStore(
        bucket_name=settings.gcs_bucket,
        watermarks_blob=settings.watermarks_blob,
        project=settings.gcp_project,
    )
