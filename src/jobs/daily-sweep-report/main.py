"""Daily sweep report job entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from daily_sweep_report.config import WATCHED_ISSUES, JobSettings
from daily_sweep_report.dates import REPORT_TZ, yesterday_range_utc
from daily_sweep_report.gmail import send_report_email
from daily_sweep_report.linear import fetch_issues, match_issues
from daily_sweep_report.report import build_email
from daily_sweep_report.secrets import load_report_secrets

logger = logging.getLogger(__name__)


def run(settings: JobSettings | None = None) -> int:
    """Fetch Linear sweep data and email the daily report."""
    cfg = settings or JobSettings.from_env()
    secrets = load_report_secrets(cfg)

    start_utc, end_utc, report_date = yesterday_range_utc()
    now = datetime.now(REPORT_TZ)

    logger.info(
        "Fetching sweep issues for %s (%s → %s UTC)",
        report_date.strftime("%A %B %-d, %Y"),
        start_utc,
        end_utc,
    )

    if cfg.skip_gcp:
        nodes: list[dict] = []
        logger.info("TOOLS_SKIP_GCP=1 — skipping Linear API call")
    else:
        nodes = fetch_issues(secrets.linear_api_key, start_utc, end_utc)

    logger.info("Found %d issue(s) in window", len(nodes))
    slots = match_issues(nodes, WATCHED_ISSUES)
    html, subject = build_email(slots, report_date, now)

    if cfg.dry_run or cfg.skip_gcp:
        logger.info("Dry run — would send: %s (%d bytes HTML)", subject, len(html))
        return 0

    send_report_email(html, subject, secrets)
    logger.info("Email sent: %s", subject)
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Send the daily Linear sweep report email")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build the report but do not send email",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    settings = JobSettings.from_env()
    if args.dry_run:
        settings = JobSettings(
            gcp_project=settings.gcp_project,
            secret_name=settings.secret_name,
            skip_gcp=settings.skip_gcp,
            dry_run=True,
        )

    sys.exit(run(settings))


if __name__ == "__main__":
    main()
