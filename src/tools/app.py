"""Minimal FastAPI app — health check + Secret Manager readiness probe."""

from __future__ import annotations

import os

from fastapi import FastAPI

from tools.config import get_settings
from tools.secrets import secret_is_accessible

app = FastAPI(title="tools-gcp", version="0.1.0")


@app.get("/health")
def health() -> dict:
    cfg = get_settings()
    return {
        "status": "ok",
        "project": cfg.gcp_project,
        "environment": cfg.environment,
    }


@app.get("/ready")
def ready() -> dict:
    configured = secret_is_accessible()
    return {
        "status": "ready" if configured else "not_ready",
        "secret_configured": configured,
    }


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("tools.app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
