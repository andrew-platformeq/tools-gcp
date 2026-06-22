"""Linear GraphQL client using urllib (stdlib) with retry on rate limits."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any

import certifi

LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class LinearClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        max_retries: int = 5,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        body = json.dumps(payload).encode("utf-8")
        last_error: Exception | None = None

        for attempt in range(max_retries):
            request = urllib.request.Request(
                LINEAR_GRAPHQL_URL,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.api_key,
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=60,
                    context=_SSL_CONTEXT,
                ) as response:
                    status_code = response.status
                    raw = response.read()
            except urllib.error.HTTPError as exc:
                status_code = exc.code
                raw = exc.read()
                if status_code == 429 and attempt < max_retries - 1:
                    sleep_s = 2 ** (attempt + 1)
                    time.sleep(sleep_s)
                    last_error = exc
                    continue
                detail = raw.decode("utf-8", errors="replace")
                msg = f"Linear API error {status_code}: {detail}"
                raise RuntimeError(msg) from exc

            if status_code == 429 and attempt < max_retries - 1:
                sleep_s = 2 ** (attempt + 1)
                time.sleep(sleep_s)
                last_error = RuntimeError("rate limited")
                continue

            if status_code >= 400:
                detail = raw.decode("utf-8", errors="replace")
                msg = f"Linear API error {status_code}: {detail}"
                raise RuntimeError(msg)

            data = json.loads(raw)
            if data.get("errors"):
                messages = [e.get("message", str(e)) for e in data["errors"]]
                raise RuntimeError("; ".join(messages))

            return data["data"]

        msg = f"request failed after retries: {last_error}"
        raise RuntimeError(msg)
