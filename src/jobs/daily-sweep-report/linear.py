"""Linear GraphQL client for sweep issues."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from daily_sweep_report.config import SWEEP_TITLES, WatchedIssue

LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"

ISSUES_QUERY = """
query($filter: IssueFilter) {
  issues(filter: $filter, first: 50) {
    nodes {
      id
      identifier
      title
      description
      completedAt
      createdAt
      assignee { name }
      state { name type }
    }
  }
}
"""


def fetch_issues(
    linear_api_key: str,
    start_utc: str,
    end_utc: str,
) -> list[dict[str, Any]]:
    """Fetch sweep issues created within the UTC time window."""
    variables = {
        "filter": {
            "createdAt": {"gte": start_utc, "lte": end_utc},
            "title": {"in": list(SWEEP_TITLES)},
        }
    }
    payload = json.dumps({"query": ISSUES_QUERY, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        LINEAR_GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": linear_api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        msg = f"Linear API error {exc.code}: {detail}"
        raise RuntimeError(msg) from exc

    if body.get("errors"):
        msg = f"Linear GraphQL errors: {body['errors']}"
        raise RuntimeError(msg)

    return body.get("data", {}).get("issues", {}).get("nodes", [])


def match_issues(
    nodes: list[dict[str, Any]],
    watched: list[WatchedIssue],
) -> list[dict[str, Any]]:
    """Pair each watched slot with a matching Linear issue, if any."""
    results: list[dict[str, Any]] = []
    for slot in watched:
        match = next(
            (
                node
                for node in nodes
                if node.get("title", "").lower() == slot["title"].lower()
                and (node.get("assignee") or {}).get("name", "").lower()
                == slot["assignee"].lower()
            ),
            None,
        )
        results.append({"watched": slot, "issue": match})
    return results
