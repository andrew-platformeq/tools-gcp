"""Insert validated telemetry events into BigQuery bronze."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Protocol

from eml_viewer_telemetry.config import Settings, get_settings
from eml_viewer_telemetry.validate import validate_batch

logger = logging.getLogger(__name__)


class BronzeWriter(Protocol):
    def insert_rows(self, rows: list[dict]) -> int: ...


class BigQueryBronzeWriter:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def insert_rows(self, rows: list[dict]) -> int:
        from google.cloud import bigquery

        client = bigquery.Client(project=self._settings.gcp_project)
        errors = client.insert_rows_json(self._settings.bronze_table_id, rows)
        if errors:
            logger.error("BigQuery insert errors: %s", errors)
            msg = "failed to insert telemetry rows into BigQuery"
            raise RuntimeError(msg)
        return len(rows)


class InMemoryBronzeWriter:
    """Test double — records rows in memory."""

    def __init__(self) -> None:
        self.rows: list[dict] = []

    def insert_rows(self, rows: list[dict]) -> int:
        self.rows.extend(rows)
        return len(rows)


def events_to_rows(events: list[dict], *, ingested_at: datetime | None = None) -> list[dict]:
    ingested = ingested_at or datetime.now(UTC)
    ingested_iso = ingested.isoformat()
    rows: list[dict] = []
    for event in events:
        rows.append(
            {
                "event_id": str(uuid.uuid4()),
                "ingested_at": ingested_iso,
                "event": event["event"],
                "ts": event["ts"],
                "user_email": event["user_email"],
                "identity_source": event["identity_source"],
                "install_id": event["install_id"],
                "session_id": event["session_id"],
                "extension_version": event["extension_version"],
                "chrome_version": event["chrome_version"],
                "platform": event["platform"],
                # BigQuery JSON columns require a JSON-encoded string for streaming insert.
                "properties": json.dumps(event.get("properties") or {}),
            }
        )
    return rows


def ingest_events(
    events: object,
    *,
    writer: BronzeWriter | None = None,
    settings: Settings | None = None,
) -> int:
    cfg = settings or get_settings()
    validated = validate_batch(events)
    rows = events_to_rows(validated)
    if writer is None:
        if cfg.skip_gcp:
            writer = InMemoryBronzeWriter()
        else:
            writer = BigQueryBronzeWriter(cfg)
    return writer.insert_rows(rows)
