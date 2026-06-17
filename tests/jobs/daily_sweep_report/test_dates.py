"""Tests for daily-sweep-report date helpers."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from daily_sweep_report.dates import REPORT_TZ, yesterday_range_utc

NY = ZoneInfo("America/New_York")


def test_monday_report_covers_previous_friday() -> None:
    # Monday 2026-06-15 10:00 ET → report date Friday 2026-06-12
    monday = datetime(2026, 6, 15, 10, 0, tzinfo=NY)
    _, _, report_date = yesterday_range_utc(now=monday)
    assert report_date.date().isoformat() == "2026-06-12"
    assert report_date.strftime("%A") == "Friday"


def test_tuesday_report_covers_monday() -> None:
    tuesday = datetime(2026, 6, 16, 10, 0, tzinfo=NY)
    _, _, report_date = yesterday_range_utc(now=tuesday)
    assert report_date.date().isoformat() == "2026-06-15"
    assert report_date.strftime("%A") == "Monday"


def test_utc_bounds_cover_full_local_day() -> None:
    tuesday = datetime(2026, 6, 16, 10, 0, tzinfo=NY)
    start_utc, end_utc, _ = yesterday_range_utc(now=tuesday)
    assert start_utc.endswith("Z")
    assert end_utc.endswith("Z")
    assert start_utc < end_utc


def test_report_tz_is_new_york() -> None:
    assert str(REPORT_TZ) == "America/New_York"
