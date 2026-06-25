"""Linear bronze extraction — backfill and incremental modes."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

from linear_ingest.client import LinearClient
from linear_ingest.config import JobSettings
from linear_ingest.entities import (
    ENTITIES,
    EPOCH,
    OVERLAP_MINUTES,
    PAGE_SIZE,
    EntityConfig,
)
from linear_ingest.gcs import BronzeStore, get_bronze_store

logger = logging.getLogger(__name__)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def parse_iso(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def format_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def max_updated_at(nodes: list[dict[str, Any]]) -> str | None:
    best: datetime | None = None
    for node in nodes:
        raw = node.get("updatedAt")
        if not raw:
            continue
        dt = parse_iso(raw)
        if best is None or dt > best:
            best = dt
    return format_iso(best) if best else None


def build_connection_query(entity: EntityConfig, with_filter: bool) -> str:
    filter_decl = ", $since: DateTimeOrDuration!" if with_filter else ""
    filter_use = ", filter: { updatedAt: { gt: $since } }" if with_filter else ""
    return f"""
    query($after: String{filter_decl}) {{
      {entity.connection}(
        first: {PAGE_SIZE}
        after: $after
        orderBy: updatedAt
        {filter_use}
      ) {{
        nodes {{
          {entity.node_fields}
        }}
        pageInfo {{
          hasNextPage
          endCursor
        }}
      }}
    }}
    """


def build_snapshot_query(entity: EntityConfig) -> str:
    return f"""
    query {{
      {entity.connection} {{
        {entity.node_fields}
      }}
    }}
    """


def pull_paginated(
    client: LinearClient,
    entity: EntityConfig,
    *,
    since: str | None,
    store: BronzeStore,
    run_prefix: str,
    run_id: str,
    mode: str,
    dry_run: bool,
) -> tuple[int, str | None]:
    query = build_connection_query(entity, with_filter=since is not None)
    after: str | None = None
    page = 0
    total = 0
    run_max: datetime | None = None

    while True:
        page += 1
        variables: dict[str, Any] = {"after": after}
        if since is not None:
            variables["since"] = since

        if dry_run and page > 1:
            break

        data = client.execute(query, variables)
        conn = data[entity.connection]
        nodes = conn["nodes"]
        page_info = conn["pageInfo"]

        for node in nodes:
            raw = node.get("updatedAt")
            if raw:
                dt = parse_iso(raw)
                if run_max is None or dt > run_max:
                    run_max = dt

        total += len(nodes)
        logger.info("  page %d: %d records", page, len(nodes))

        if not dry_run:
            store.write_bronze_page(
                run_prefix=run_prefix,
                entity=entity.name,
                page=page,
                payload={
                    "meta": {
                        "run_id": run_id,
                        "entity": entity.name,
                        "mode": mode,
                        "page": page,
                        "since": since,
                        "extracted_at": utc_now_iso(),
                        "record_count": len(nodes),
                    },
                    "nodes": nodes,
                },
            )

        if dry_run or not page_info["hasNextPage"]:
            break

        after = page_info["endCursor"]

    return total, format_iso(run_max) if run_max else None


def pull_snapshot(
    client: LinearClient,
    entity: EntityConfig,
    *,
    store: BronzeStore,
    run_prefix: str,
    run_id: str,
    mode: str,
    dry_run: bool,
) -> tuple[int, str | None]:
    data = client.execute(build_snapshot_query(entity))
    obj = data[entity.connection]
    nodes = [obj]
    logger.info("  snapshot: 1 record")
    if not dry_run:
        store.write_bronze_page(
            run_prefix=run_prefix,
            entity=entity.name,
            page=1,
            payload={
                "meta": {
                    "run_id": run_id,
                    "entity": entity.name,
                    "mode": mode,
                    "page": 1,
                    "since": None,
                    "extracted_at": utc_now_iso(),
                    "record_count": 1,
                },
                "nodes": nodes,
            },
        )
    raw = obj.get("updatedAt")
    return 1, raw


def resolve_since(
    entity: EntityConfig,
    watermarks: dict[str, Any],
    *,
    mode: str,
    override_since: str | None,
) -> str | None:
    if not entity.incremental or mode == "backfill":
        return None
    if override_since:
        return override_since

    entry = watermarks["entities"].get(entity.name)
    if not entry or not entry.get("watermark_at"):
        logger.warning(
            "  no watermark for %s; using epoch (full history). "
            "Run backfill first to establish baselines.",
        )
        return EPOCH

    wm = parse_iso(entry["watermark_at"])
    return format_iso(wm - timedelta(minutes=OVERLAP_MINUTES))


def run_extract(
    client: LinearClient,
    *,
    mode: str,
    settings: JobSettings,
    dry_run: bool,
    override_since: str | None,
    entities_filter: list[str] | None,
    store: BronzeStore | None = None,
) -> dict[str, Any]:
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_prefix = f"{'backfill' if mode == 'backfill' else 'daily'}/{run_id}"
    bronze_store = store or get_bronze_store(settings)
    watermarks = bronze_store.load_watermarks()

    selected = ENTITIES
    if entities_filter:
        allowed = set(entities_filter)
        selected = [e for e in ENTITIES if e.name in allowed]
        missing = allowed - {e.name for e in selected}
        if missing:
            raise ValueError(f"unknown entities: {', '.join(sorted(missing))}")

    summary: dict[str, Any] = {
        "run_id": run_id,
        "mode": mode,
        "dry_run": dry_run,
        "started_at": utc_now_iso(),
        "run_prefix": run_prefix,
        "entities": {},
    }

    logger.info("Run %s (%s)%s", run_id, mode, " [dry-run]" if dry_run else "")

    for entity in selected:
        since = resolve_since(
            entity, watermarks, mode=mode, override_since=override_since
        )
        label = entity.name
        if since:
            logger.info("%s (since %s)", label, since)
        else:
            logger.info("%s (full snapshot)", label)

        try:
            if entity.paginated:
                count, new_wm = pull_paginated(
                    client,
                    entity,
                    since=since,
                    store=bronze_store,
                    run_prefix=run_prefix,
                    run_id=run_id,
                    mode=mode,
                    dry_run=dry_run,
                )
            else:
                count, new_wm = pull_snapshot(
                    client,
                    entity,
                    store=bronze_store,
                    run_prefix=run_prefix,
                    run_id=run_id,
                    mode=mode,
                    dry_run=dry_run,
                )
        except Exception as exc:
            logger.error("  FAILED: %s", exc)
            summary["entities"][label] = {"status": "failed", "error": str(exc)}
            summary["status"] = "partial_failure"
            continue

        entity_result: dict[str, Any] = {
            "status": "success",
            "records": count,
            "since": since,
            "new_watermark": new_wm,
        }
        summary["entities"][label] = entity_result

        if not dry_run:
            effective_wm = new_wm
            if not effective_wm and entity.incremental:
                effective_wm = utc_now_iso()
                entity_result["new_watermark"] = effective_wm
            elif effective_wm and entity.incremental:
                old_wm = watermarks["entities"].get(label, {}).get("watermark_at")
                if old_wm and effective_wm == old_wm:
                    effective_wm = utc_now_iso()
                    entity_result["new_watermark"] = effective_wm

            if effective_wm:
                watermarks["entities"].setdefault(label, {})
                watermarks["entities"][label].update(
                    {
                        "watermark_at": effective_wm,
                        "last_run_id": run_id,
                        "last_success_at": utc_now_iso(),
                        "last_record_count": count,
                    }
                )
                bronze_store.save_watermarks(watermarks)
                logger.info("  watermark → %s", effective_wm)

    summary["completed_at"] = utc_now_iso()
    if "status" not in summary:
        summary["status"] = "success"

    if not dry_run:
        summary_path = bronze_store.write_summary(run_prefix, summary)
        logger.info("Summary: %s", summary_path)

    return summary


def print_results(summary: dict[str, Any]) -> None:
    print("\nResults:")
    for name, result in summary["entities"].items():
        if result.get("status") == "success":
            print(f"  {name}: {result['records']} records")
        else:
            print(f"  {name}: FAILED — {result.get('error')}", file=sys.stderr)
