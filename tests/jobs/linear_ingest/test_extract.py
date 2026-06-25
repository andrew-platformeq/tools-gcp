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
from linear_ingest.extract import resolve_since, run_extract
from linear_ingest.gcs import LocalBronzeStore
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
