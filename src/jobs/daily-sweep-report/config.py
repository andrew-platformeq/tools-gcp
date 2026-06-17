"""Non-secret configuration for the daily sweep report job."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TypedDict


class WatchedIssue(TypedDict):
    title: str
    assignee: str


# Issues to track — titles and assignees must match Linear exactly.
WATCHED_ISSUES: list[WatchedIssue] = [
    {"title": "Beginning of Day Sweep", "assignee": "Marco Durante"},
    {"title": "End of Day Sweep", "assignee": "Marco Durante"},
    {"title": "Beginning of Day Sweep", "assignee": "Amer Roufail"},
    {"title": "End of Day Sweep", "assignee": "Amer Roufail"},
]

SWEEP_TITLES = ("Beginning of Day Sweep", "End of Day Sweep")

DEFAULT_SECRET_NAME = "peq-tools-daily-sweep-report-config"


@dataclass(frozen=True)
class JobSettings:
    gcp_project: str
    secret_name: str
    skip_gcp: bool
    dry_run: bool

    @classmethod
    def from_env(cls) -> JobSettings:
        return cls(
            gcp_project=os.environ.get("TOOLS_GCP_PROJECT", "peq-tools"),
            secret_name=os.environ.get(
                "TOOLS_DAILY_SWEEP_REPORT_SECRET_NAME",
                DEFAULT_SECRET_NAME,
            ),
            skip_gcp=os.environ.get("TOOLS_SKIP_GCP", "").lower() in ("1", "true", "yes"),
            dry_run=os.environ.get("TOOLS_DAILY_SWEEP_REPORT_DRY_RUN", "").lower()
            in ("1", "true", "yes"),
        )


@dataclass(frozen=True)
class ReportSecrets:
    gmail_address: str
    gmail_app_password: str
    send_to: str
    linear_api_key: str

    @classmethod
    def from_mapping(cls, data: dict[str, str]) -> ReportSecrets:
        missing = [
            key
            for key in ("gmail_address", "gmail_app_password", "send_to", "linear_api_key")
            if not data.get(key)
        ]
        if missing:
            msg = f"Secret JSON missing required keys: {', '.join(missing)}"
            raise ValueError(msg)
        return cls(
            gmail_address=data["gmail_address"],
            gmail_app_password=data["gmail_app_password"],
            send_to=data["send_to"],
            linear_api_key=data["linear_api_key"],
        )
