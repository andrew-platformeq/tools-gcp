"""Tests for daily-sweep-report Linear matching and HTML."""

from __future__ import annotations

from datetime import datetime

from daily_sweep_report.config import WATCHED_ISSUES, ReportSecrets
from daily_sweep_report.dates import REPORT_TZ
from daily_sweep_report.linear import match_issues
from daily_sweep_report.main import run
from daily_sweep_report.report import build_email


def test_match_issues_pairs_by_title_and_assignee() -> None:
    nodes = [
        {
            "title": "Beginning of Day Sweep",
            "assignee": {"name": "Marco Durante"},
            "state": {"type": "completed"},
            "identifier": "PEQ-1",
            "completedAt": "2026-06-12T14:00:00Z",
            "description": "All clear",
            "url": "https://linear.app/issue/1",
        }
    ]
    slots = match_issues(nodes, WATCHED_ISSUES)
    assert len(slots) == 4
    marco_bod = next(
        s
        for s in slots
        if s["watched"]["assignee"] == "Marco Durante"
        and s["watched"]["title"] == "Beginning of Day Sweep"
    )
    assert marco_bod["issue"] is not None
    assert marco_bod["issue"]["identifier"] == "PEQ-1"


def test_build_email_subject_and_counts() -> None:
    slots = match_issues([], WATCHED_ISSUES)
    report_date = datetime(2026, 6, 12, tzinfo=REPORT_TZ)
    generated = datetime(2026, 6, 15, 9, 0, tzinfo=REPORT_TZ)
    html, subject = build_email(slots, report_date, generated)
    assert subject == "[Jun 12, 2026] Sweep Report"
    assert "Missing" in html
    assert "Marco Durante" in html
    assert "Amer Roufail" in html


def test_report_secrets_requires_all_keys() -> None:
    try:
        ReportSecrets.from_mapping({"gmail_address": "a@b.com"})
    except ValueError as exc:
        assert "linear_api_key" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_run_skip_gcp_does_not_send() -> None:
    from daily_sweep_report.config import JobSettings

    settings = JobSettings(
        gcp_project="test",
        secret_name="test-secret",
        skip_gcp=True,
        dry_run=False,
    )
    assert run(settings) == 0
