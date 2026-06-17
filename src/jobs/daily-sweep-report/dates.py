"""Report date range helpers (America/New_York, Mon reports prior Friday)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

REPORT_TZ = ZoneInfo("America/New_York")


def yesterday_range_utc(
    now: datetime | None = None,
) -> tuple[str, str, datetime]:
    """Return UTC ISO bounds and the report date in local time.

    On Monday the report covers Friday (3 days back). Otherwise yesterday.
    """
    now_local = (now or datetime.now(REPORT_TZ)).astimezone(REPORT_TZ)
    days_back = 3 if now_local.weekday() == 0 else 1
    report_date = now_local - timedelta(days=days_back)

    start_local = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = report_date.replace(hour=23, minute=59, second=59, microsecond=0)

    start_utc = start_local.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_utc = end_local.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return start_utc, end_utc, report_date
