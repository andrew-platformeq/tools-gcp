"""Tests run without GCP credentials (TOOLS_SKIP_GCP=1)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ["TOOLS_SKIP_GCP"] = "1"
os.environ["TOOLS_GCP_PROJECT"] = "test-project"

from tools.app import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["project"] == "test-project"
    assert body["environment"] == "nonprod"


def test_ready_skips_gcp(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["secret_configured"] is True


def test_ready_secret_not_accessible(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TOOLS_SKIP_GCP", "0")
    monkeypatch.setattr("tools.app.secret_is_accessible", lambda: False)

    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["secret_configured"] is False
