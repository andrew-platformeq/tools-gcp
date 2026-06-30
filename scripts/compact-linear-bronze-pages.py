#!/usr/bin/env python3
"""Rewrite bronze page_*.json files as compact single-line JSON for BigQuery.

BigQuery external JSON tables read one JSON object per line. Older ingest runs wrote
pretty-printed multi-line files; this script re-encodes them in place (same path).

Usage:
  python scripts/compact-linear-bronze-pages.py --bucket peq-tools-linear-data
  python scripts/compact-linear-bronze-pages.py --bucket peq-tools-linear-data --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys

from google.cloud import storage


def compact_blob(blob: storage.Blob, *, dry_run: bool) -> bool:
    """Return True if blob was (or would be) rewritten."""
    raw = blob.download_as_text(encoding="utf-8")
    if "\n" not in raw.strip():
        return False
    data = json.loads(raw)
    compact = json.dumps(data, separators=(",", ":")) + "\n"
    if compact == raw:
        return False
    if not dry_run:
        blob.upload_from_string(compact, content_type="application/json")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", default="peq-tools-linear-data")
    parser.add_argument("--prefix", default="bronze/")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    client = storage.Client()
    bucket = client.bucket(args.bucket)
    scanned = 0
    rewritten = 0

    for blob in client.list_blobs(args.bucket, prefix=args.prefix):
        if "/page_" not in blob.name or not blob.name.endswith(".json"):
            continue
        scanned += 1
        if compact_blob(blob, dry_run=args.dry_run):
            rewritten += 1
            action = "would rewrite" if args.dry_run else "rewrote"
            print(f"{action}: gs://{args.bucket}/{blob.name}")

    label = "Would rewrite" if args.dry_run else "Rewrote"
    print(f"{label} {rewritten} of {scanned} bronze page file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
