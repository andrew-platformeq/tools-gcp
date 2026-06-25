"""Tests for eml-viewer-telemetry ingest and API."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ["TOOLS_SKIP_GCP"] = "1"
os.environ["TOOLS_GCP_PROJECT"] = "test-project"
os.environ["TOOLS_EML_VIEWER_TELEMETRY_TEST_API_KEY"] = "test-telemetry-key"

from eml_viewer_telemetry.app import app  # noqa: E402
from eml_viewer_telemetry.ingest import InMemoryBronzeWriter, ingest_events  # noqa: E402
from eml_viewer_telemetry.validate import validate_batch  # noqa: E402

SAMPLE_EVENT = {
    "event": "import_succeeded",
    "ts": "2026-06-23T19:35:51.224Z",
    "user_email": "jane@platformeq.com",
    "identity_source": "chrome",
    "install_id": "6733d244-539b-4daa-81d9-c02d0c5217db",
    "session_id": "3bb0202d-3f42-4eb0-885b-b30fdb5dff35",
    "extension_version": "0.1.0",
    "chrome_version": "149.0.0.0",
    "platform": "MacIntel",
    "properties": {
        "content_fingerprint": "abc123",
        "method": "picker",
        "file_size_bucket": "0-100kb",
    },
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_validate_rejects_forbidden_properties() -> None:
    bad = {**SAMPLE_EVENT, "properties": {"subject": "secret"}}
    with pytest.raises(ValueError, match="forbidden"):
        validate_batch([bad])


def test_ingest_writes_rows_to_memory() -> None:
    writer = InMemoryBronzeWriter()
    count = ingest_events([SAMPLE_EVENT], writer=writer)
    assert count == 1
    assert writer.rows[0]["event"] == "import_succeeded"
    assert writer.rows[0]["properties"]["method"] == "picker"


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "eml-viewer-telemetry"


def test_ingest_requires_auth(client: TestClient) -> None:
    response = client.post("/v1/eml-viewer/telemetry", json={"events": [SAMPLE_EVENT]})
    assert response.status_code == 401


def test_ingest_accepts_valid_batch(client: TestClient) -> None:
    response = client.post(
        "/v1/eml-viewer/telemetry",
        headers={"Authorization": "Bearer test-telemetry-key"},
        json={"events": [SAMPLE_EVENT]},
    )
    assert response.status_code == 200
    assert response.json()["inserted"] == 1


def test_ingest_rejects_bad_payload(client: TestClient) -> None:
    bad = {**SAMPLE_EVENT, "properties": {"filename": "patient.eml"}}
    response = client.post(
        "/v1/eml-viewer/telemetry",
        headers={"Authorization": "Bearer test-telemetry-key"},
        json={"events": [bad]},
    )
    assert response.status_code == 400
