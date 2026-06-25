"""Linear bronze ingest job entry point."""

from __future__ import annotations

import argparse
import logging
import sys

from linear_ingest.client import LinearClient
from linear_ingest.config import JobSettings
from linear_ingest.extract import print_results, run_extract
from linear_ingest.secrets import load_ingest_secrets


def run(
    mode: str,
    *,
    settings: JobSettings | None = None,
    dry_run: bool = False,
    override_since: str | None = None,
    entities_filter: list[str] | None = None,
) -> int:
    cfg = settings or JobSettings.from_env()
    if dry_run:
        cfg = JobSettings(
            gcp_project=cfg.gcp_project,
            gcs_bucket=cfg.gcs_bucket,
            watermarks_blob=cfg.watermarks_blob,
            secret_name=cfg.secret_name,
            skip_gcp=cfg.skip_gcp,
            dry_run=True,
        )

    secrets = load_ingest_secrets(cfg)
    client = LinearClient(secrets.linear_api_key)

    summary = run_extract(
        client,
        mode=mode,
        settings=cfg,
        dry_run=dry_run or cfg.dry_run,
        override_since=override_since,
        entities_filter=entities_filter,
    )
    print_results(summary)
    return 0 if summary.get("status") == "success" else 1


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Extract Linear data to bronze JSON in GCS.",
    )
    parser.add_argument(
        "mode",
        choices=["backfill", "incremental"],
        help="backfill = full history; incremental = watermark-based delta",
    )
    parser.add_argument(
        "--since",
        help="override watermark with explicit ISO timestamp (incremental only)",
    )
    parser.add_argument(
        "--entities",
        help="comma-separated entity subset (e.g. issues,comments)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="fetch first page only; do not write bronze or update watermarks",
    )
    args = parser.parse_args(argv)

    if args.since and args.mode != "incremental":
        parser.error("--since is only valid with incremental mode")

    entities_filter = None
    if args.entities:
        entities_filter = [e.strip() for e in args.entities.split(",") if e.strip()]

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    sys.exit(
        run(
            args.mode,
            dry_run=args.dry_run,
            override_since=args.since,
            entities_filter=entities_filter,
        )
    )


if __name__ == "__main__":
    main()
