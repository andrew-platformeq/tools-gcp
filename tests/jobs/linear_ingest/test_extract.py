"""Tests for linear-ingest extraction and storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from linear_ingest.client import LinearClient
from linear_ingest.config import IngestSecrets, JobSettings
from linear_ingest.entities import EPOCH, EntityConfig
from linear_ingest.extract import (
    build_connection_query,
    build_run_history_record,
    resolve_since,
    run_extract,
)
from linear_ingest.gcs import RUN_HISTORY_PREFIX, LocalBronzeStore
from linear_ingest.main import run


class FakeLinearClient:
    def __init__(self, responses: dict[str, Any]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        max_retries: int = 5,
    ) -> dict[str, Any]:
        self.calls.append((query, variables))
        for key, value in self.responses.items():
            if key in query:
                return value
        raise RuntimeError(f"unexpected query: {query[:80]}")


ORG_RESPONSE = {
    "organization": {
        "id": "org-1",
        "name": "PEQ",
        "updatedAt": "2026-06-01T00:00:00.000Z",
    }
}

TEAMS_RESPONSE = {
    "teams": {
        "nodes": [
            {"id": "t1", "name": "Eng", "updatedAt": "2026-06-10T12:00:00.000Z"},
        ],
        "pageInfo": {"hasNextPage": False, "endCursor": "c1"},
    }
}


def test_ingest_secrets_requires_linear_api_key() -> None:
    with pytest.raises(ValueError, match="linear_api_key"):
        IngestSecrets.from_mapping({})


def test_resolve_since_backfill_returns_none() -> None:
    entity = EntityConfig(
        name="issues",
        connection="issues",
        node_fields="id updatedAt",
    )
    watermarks = {"entities": {"issues": {"watermark_at": "2026-06-01T00:00:00.000Z"}}}
    assert resolve_since(entity, watermarks, mode="backfill", override_since=None) is None


def test_resolve_since_incremental_applies_overlap() -> None:
    entity = EntityConfig(
        name="issues",
        connection="issues",
        node_fields="id updatedAt",
    )
    watermarks = {"entities": {"issues": {"watermark_at": "2026-06-10T12:10:00.000Z"}}}
    since = resolve_since(entity, watermarks, mode="incremental", override_since=None)
    assert since == "2026-06-10T12:05:00.000Z"


def test_resolve_since_missing_watermark_uses_epoch() -> None:
    entity = EntityConfig(
        name="issues",
        connection="issues",
        node_fields="id updatedAt",
    )
    since = resolve_since(entity, {"entities": {}}, mode="incremental", override_since=None)
    assert since == EPOCH


def test_run_extract_backfill_writes_bronze_and_watermarks(tmp_path: Path) -> None:
    store = LocalBronzeStore(root=tmp_path)
    client = FakeLinearClient({"organization": ORG_RESPONSE, "teams": TEAMS_RESPONSE})
    settings = JobSettings(
        gcp_project="test",
        gcs_bucket="test-bucket",
        watermarks_blob="state/watermarks.json",
        secret_name="test-secret",
        skip_gcp=True,
        dry_run=False,
    )

    summary = run_extract(
        client,  # type: ignore[arg-type]
        mode="backfill",
        settings=settings,
        dry_run=False,
        override_since=None,
        entities_filter=["organization", "teams"],
        store=store,
    )

    assert summary["status"] == "success"
    assert summary["entities"]["organization"]["records"] == 1
    assert summary["entities"]["teams"]["records"] == 1

    wm = store.load_watermarks()
    assert "teams" in wm["entities"]
    assert wm["entities"]["teams"]["watermark_at"] == "2026-06-10T12:00:00.000Z"

    bronze_files = list(tmp_path.rglob("page_*.json"))
    assert len(bronze_files) == 2


def test_run_extract_dry_run_skips_writes(tmp_path: Path) -> None:
    store = LocalBronzeStore(root=tmp_path)
    client = FakeLinearClient({"teams": TEAMS_RESPONSE})

    summary = run_extract(
        client,  # type: ignore[arg-type]
        mode="incremental",
        settings=JobSettings(
            gcp_project="test",
            gcs_bucket="test-bucket",
            watermarks_blob="state/watermarks.json",
            secret_name="test-secret",
            skip_gcp=True,
            dry_run=True,
        ),
        dry_run=True,
        override_since=None,
        entities_filter=["teams"],
        store=store,
    )

    assert summary["status"] == "success"
    assert summary["dry_run"] is True
    assert not list(tmp_path.rglob("page_*.json"))
    assert not store.watermarks_path.exists()


def test_run_skip_gcp_dry_run(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.execute.return_value = TEAMS_RESPONSE
    monkeypatch.setattr("linear_ingest.main.LinearClient", lambda key: fake_client)

    settings = JobSettings(
        gcp_project="test",
        gcs_bucket="test-bucket",
        watermarks_blob="state/watermarks.json",
        secret_name="test-secret",
        skip_gcp=True,
        dry_run=True,
    )
    assert run("incremental", settings=settings, dry_run=True, entities_filter=["teams"]) == 0


def test_linear_client_parses_success(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = json.dumps({"data": {"teams": {"nodes": [], "pageInfo": {}}}}).encode()

    class FakeResponse:
        status = 200

        def read(self) -> bytes:
            return payload

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            pass

    monkeypatch.setattr(
        "linear_ingest.client.urllib.request.urlopen",
        lambda *a, **k: FakeResponse(),
    )
    data = LinearClient("key").execute("query { teams { nodes { id } } }")
    assert "teams" in data


def test_build_connection_query_includes_archived() -> None:
    entity = EntityConfig(name="issues", connection="issues", node_fields="id updatedAt")
    # Required so backfills don't silently skip archived records (archiving doesn't bump
    # updatedAt and archived rows are excluded from the default connection).
    assert "includeArchived: true" in build_connection_query(entity, with_filter=False)
    assert "includeArchived: true" in build_connection_query(entity, with_filter=True)


def test_build_run_history_record_flattens_and_rolls_up() -> None:
    summary = {
        "run_id": "run_X",
        "mode": "incremental",
        "dry_run": False,
        "status": "partial_failure",
        "started_at": "2026-06-25T00:00:00.000Z",
        "completed_at": "2026-06-25T00:01:00.000Z",
        "run_prefix": "daily/run_X",
        "entities": {
            "issues": {"status": "success", "records": 7, "since": None, "new_watermark": "w"},
            "comments": {"status": "failed", "error": "boom"},
        },
    }
    record = build_run_history_record(summary)

    assert record["run_id"] == "run_X"
    assert record["total_records"] == 7
    assert record["entity_failures"] == 1
    # entities is a uniform list of structs, not a map keyed by name.
    assert isinstance(record["entities"], list)
    by_name = {e["entity"]: e for e in record["entities"]}
    assert by_name["issues"]["records"] == 7
    assert by_name["comments"]["error"] == "boom"
    assert "code_version" in record


def test_run_extract_writes_run_history(tmp_path: Path) -> None:
    store = LocalBronzeStore(root=tmp_path)
    client = FakeLinearClient({"organization": ORG_RESPONSE, "teams": TEAMS_RESPONSE})
    settings = JobSettings(
        gcp_project="test",
        gcs_bucket="test-bucket",
        watermarks_blob="state/watermarks.json",
        secret_name="test-secret",
        skip_gcp=True,
        dry_run=False,
    )

    summary = run_extract(
        client,  # type: ignore[arg-type]
        mode="backfill",
        settings=settings,
        dry_run=False,
        override_since=None,
        entities_filter=["organization", "teams"],
        store=store,
    )

    history_files = list((tmp_path / RUN_HISTORY_PREFIX).glob("*.json"))
    assert len(history_files) == 1
    # Append-only: the file name is the run id, and the body is one NDJSON record.
    assert history_files[0].name == f"{summary['run_id']}.json"
    lines = history_files[0].read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["run_id"] == summary["run_id"]
    assert record["total_records"] == 2
