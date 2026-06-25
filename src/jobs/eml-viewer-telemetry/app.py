"""Public Cloud Run service for EML Viewer extension telemetry ingest."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from eml_viewer_telemetry.config import get_settings
from eml_viewer_telemetry.ingest import ingest_events
from eml_viewer_telemetry.secrets import load_telemetry_secrets
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

app = FastAPI(title="eml-viewer-telemetry", version="0.1.0")

_api_key: str | None = None


class TelemetryBatch(BaseModel):
    events: list[dict[str, Any]] = Field(min_length=1, max_length=500)


def _expected_api_key() -> str:
    global _api_key
    if _api_key is None:
        _api_key = load_telemetry_secrets().api_key
    return _api_key


def _authorize(authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if not token or token != _expected_api_key():
        raise HTTPException(status_code=401, detail="invalid api key")


@app.get("/health")
def health() -> dict[str, str]:
    cfg = get_settings()
    return {
        "status": "ok",
        "project": cfg.gcp_project,
        "environment": cfg.environment,
        "service": "eml-viewer-telemetry",
    }


@app.post("/v1/eml-viewer/telemetry")
def ingest_telemetry(
    batch: TelemetryBatch,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, int]:
    _authorize(authorization)
    try:
        inserted = ingest_events(batch.events)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("telemetry ingest failed")
        raise HTTPException(status_code=500, detail="ingest failed") from exc
    return {"inserted": inserted}


def main() -> None:
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("eml_viewer_telemetry.app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
