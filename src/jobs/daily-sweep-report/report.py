"""HTML email builder for the daily sweep report."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

REPORT_TZ = ZoneInfo("America/New_York")


def _fmt_time(iso: str | None, tz: ZoneInfo) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(tz)
        return dt.strftime("%-I:%M %p %Z")
    except ValueError:
        return "—"


def _extract_notes(description: str | None) -> str:
    notes: list[str] = []
    for line in (description or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("- [ ]", "- [x]", "- [X]")):
            continue
        notes.append(stripped)
    return " ".join(notes).strip()


def _issue_row_html(slot: dict[str, Any], tz: ZoneInfo) -> str:
    issue = slot.get("issue")
    watched = slot["watched"]
    title = watched["title"]

    if issue is None:
        return f"""
        <div style="padding:14px 18px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="width:28px;height:28px;background:#f4f4f8;border-radius:7px;text-align:center;vertical-align:middle;font-size:13px;">—</td>
              <td style="padding-left:10px;">
                <div style="font-size:13px;font-weight:600;color:#1a1a2e;">{title}</div>
                <div style="font-family:monospace;font-size:10px;color:#b0b0cc;margin-top:2px;">No issue created for this day</div>
              </td>
              <td style="text-align:right;white-space:nowrap;">
                <span style="background:#f4f4f8;border:1px solid #ddddf0;border-radius:100px;padding:4px 10px;font-family:monospace;font-size:9px;color:#9999bb;letter-spacing:.1em;text-transform:uppercase;">● Missing</span>
              </td>
            </tr>
          </table>
          <div style="margin-top:10px;margin-left:38px;background:#f4f4f8;border:1px solid #e0e0f0;border-radius:8px;padding:10px 14px;font-size:12px;color:#9999bb;">This issue was not created on this day.</div>
        </div>"""

    state_type = (issue.get("state") or {}).get("type", "")
    is_done = state_type == "completed"
    identifier = issue.get("identifier", "—")
    url = issue.get("url", "#")
    note_text = _extract_notes(issue.get("description"))

    if is_done:
        time_str = _fmt_time(issue.get("completedAt"), tz)
        if note_text:
            note_box = f"""<div style="margin-top:10px;margin-left:38px;background:#f7f7fc;border:1px solid #e8e8f2;border-radius:8px;padding:10px 14px;font-size:12px;color:#4a4a6a;">{note_text}</div>"""
        else:
            note_box = """<div style="margin-top:10px;margin-left:38px;background:#f7f7fc;border:1px solid #e8e8f2;border-radius:8px;padding:10px 14px;font-size:12px;color:#9999bb;">Completed with no additional notes.</div>"""
        return f"""
        <div style="padding:14px 18px;border-bottom:1px solid #f0f0f8;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="width:28px;height:28px;background:#f0fdf8;border-radius:7px;text-align:center;vertical-align:middle;font-size:13px;">✅</td>
              <td style="padding-left:10px;">
                <div style="font-size:13px;font-weight:600;color:#1a1a2e;">{title}</div>
                <div style="font-family:monospace;font-size:10px;color:#b0b0cc;margin-top:2px;">{identifier} · Completed {time_str}</div>
              </td>
              <td style="text-align:right;white-space:nowrap;">
                <span style="background:#f0fdf8;border:1px solid #a7f3d0;border-radius:100px;padding:4px 10px;font-family:monospace;font-size:9px;color:#059669;letter-spacing:.1em;text-transform:uppercase;">● Done</span>
              </td>
            </tr>
          </table>
          {note_box}
          <div style="margin-top:8px;margin-left:38px;"><a href="{url}" style="font-family:monospace;font-size:10px;color:#7c6bff;text-decoration:none;">View in Linear ↗</a></div>
        </div>"""

    return f"""
    <div style="padding:14px 18px;border-bottom:1px solid #f0f0f8;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="width:28px;height:28px;background:#fffbeb;border-radius:7px;text-align:center;vertical-align:middle;font-size:13px;">⏳</td>
          <td style="padding-left:10px;">
            <div style="font-size:13px;font-weight:600;color:#1a1a2e;">{title}</div>
            <div style="font-family:monospace;font-size:10px;color:#b0b0cc;margin-top:2px;">{identifier} · Not completed</div>
          </td>
          <td style="text-align:right;white-space:nowrap;">
            <span style="background:#fffbeb;border:1px solid #fde68a;border-radius:100px;padding:4px 10px;font-family:monospace;font-size:9px;color:#d97706;letter-spacing:.1em;text-transform:uppercase;">● Pending</span>
          </td>
        </tr>
      </table>
      <div style="margin-top:10px;margin-left:38px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:10px 14px;font-size:12px;color:#92400e;">Not completed — this sweep was not marked Done by end of day.</div>
      <div style="margin-top:8px;margin-left:38px;"><a href="{url}" style="font-family:monospace;font-size:10px;color:#7c6bff;text-decoration:none;">View in Linear ↗</a></div>
    </div>"""


def _person_block_html(
    name: str,
    initials: str,
    avatar_color: str,
    slots: list[dict[str, Any]],
    tz: ZoneInfo,
) -> str:
    done_count = sum(
        1
        for slot in slots
        if slot.get("issue") and (slot["issue"].get("state") or {}).get("type") == "completed"
    )
    total = len(slots)
    rows = "".join(_issue_row_html(slot, tz) for slot in slots)
    return f"""
    <p style="font-family:monospace;font-size:9px;letter-spacing:.2em;color:#b0b0cc;text-transform:uppercase;margin:0 0 10px;">{name}</p>
    <div style="border:1.5px solid #e8e8f2;border-radius:12px;overflow:hidden;margin-bottom:28px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7fc;border-bottom:1px solid #e8e8f2;">
        <tr>
          <td style="padding:14px 18px;">
            <table cellpadding="0" cellspacing="0"><tr>
              <td style="width:34px;height:34px;background:{avatar_color};border-radius:50%;text-align:center;vertical-align:middle;font-size:12px;font-weight:700;color:#fff;padding:0;">{initials}</td>
              <td style="padding-left:10px;">
                <div style="font-size:14px;font-weight:600;color:#1a1a2e;">{name}</div>
                <div style="font-family:monospace;font-size:10px;color:#b0b0cc;letter-spacing:.06em;">Team Member · Mekhael</div>
              </td>
            </tr></table>
          </td>
          <td style="padding:14px 18px;text-align:right;font-family:monospace;font-size:11px;color:#b0b0cc;">{done_count} / {total} complete</td>
        </tr>
      </table>
      <div style="background:#fff;">{rows}</div>
    </div>"""


def build_email(
    slots: list[dict[str, Any]],
    report_date: datetime,
    generated_at: datetime,
    tz: ZoneInfo = REPORT_TZ,
) -> tuple[str, str]:
    """Build HTML body and subject for the sweep report."""
    done_count = sum(
        1
        for slot in slots
        if slot.get("issue") and (slot["issue"].get("state") or {}).get("type") == "completed"
    )
    pending_count = sum(
        1
        for slot in slots
        if slot.get("issue") and (slot["issue"].get("state") or {}).get("type") != "completed"
    )
    missing_count = sum(1 for slot in slots if not slot.get("issue"))
    total = len(slots)
    progress_pct = int((done_count / total) * 100) if total else 0

    report_local = report_date.astimezone(tz)
    generated_local = generated_at.astimezone(tz)

    date_str = report_local.strftime("%B %-d, %Y")
    day_str = report_local.strftime("%A, %B %-d %Y")
    gen_time_str = generated_local.strftime("%-I:%M %p %Z")
    subject_date = report_local.strftime("%b %-d, %Y")

    marco_slots = [s for s in slots if s["watched"]["assignee"] == "Marco Durante"]
    amer_slots = [s for s in slots if s["watched"]["assignee"] == "Amer Roufail"]

    marco_block = _person_block_html(
        "Marco Durante",
        "MD",
        "linear-gradient(135deg,#7c6bff,#5b4fd4)",
        marco_slots,
        tz,
    )
    amer_block = _person_block_html(
        "Amer Roufail",
        "AR",
        "linear-gradient(135deg,#06b6d4,#0891b2)",
        amer_slots,
        tz,
    )

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f0f6;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<div style="max-width:620px;margin:0 auto;padding:32px 16px;">
  <p style="font-family:monospace;font-size:10px;letter-spacing:.18em;color:#9999bb;text-transform:uppercase;margin:0 0 10px;">Mekhael · Linear · Automated Report</p>
  <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 32px rgba(0,0,0,0.09);">
    <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);padding:30px 34px 26px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <div style="width:7px;height:7px;background:#9d8fff;border-radius:50%;display:inline-block;margin-right:6px;"></div>
        <span style="font-family:monospace;font-size:10px;color:#9d8fff;letter-spacing:.16em;text-transform:uppercase;">Daily Sweep Report</span>
      </div>
      <div style="font-size:22px;font-weight:700;color:#fff;letter-spacing:-.025em;margin-bottom:8px;">[{subject_date}] Sweep Report</div>
      <div style="margin-bottom:22px;">
        <span style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:100px;padding:4px 10px;font-family:monospace;font-size:10px;color:rgba(255,255,255,0.45);margin-right:6px;">{day_str}</span>
        <span style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:100px;padding:4px 10px;font-family:monospace;font-size:10px;color:rgba(255,255,255,0.45);margin-right:6px;">Team Mekhael</span>
        <span style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:100px;padding:4px 10px;font-family:monospace;font-size:10px;color:rgba(255,255,255,0.45);">Generated {gen_time_str}</span>
      </div>
      <table width="100%" cellpadding="0" cellspacing="8" style="border-collapse:separate;border-spacing:8px;">
        <tr>
          <td style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:12px 10px;text-align:center;">
            <div style="font-size:24px;font-weight:700;color:#34d399;line-height:1;margin-bottom:4px;">{done_count}</div>
            <div style="font-family:monospace;font-size:9px;letter-spacing:.1em;color:rgba(255,255,255,0.28);text-transform:uppercase;">Done</div>
          </td>
          <td style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:12px 10px;text-align:center;">
            <div style="font-size:24px;font-weight:700;color:#fbbf24;line-height:1;margin-bottom:4px;">{pending_count}</div>
            <div style="font-family:monospace;font-size:9px;letter-spacing:.1em;color:rgba(255,255,255,0.28);text-transform:uppercase;">Pending</div>
          </td>
          <td style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:12px 10px;text-align:center;">
            <div style="font-size:24px;font-weight:700;color:rgba(255,255,255,0.35);line-height:1;margin-bottom:4px;">{missing_count}</div>
            <div style="font-family:monospace;font-size:9px;letter-spacing:.1em;color:rgba(255,255,255,0.28);text-transform:uppercase;">Missing</div>
          </td>
          <td style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:12px 10px;text-align:center;">
            <div style="font-size:24px;font-weight:700;color:rgba(255,255,255,0.35);line-height:1;margin-bottom:4px;">{total}</div>
            <div style="font-family:monospace;font-size:9px;letter-spacing:.1em;color:rgba(255,255,255,0.28);text-transform:uppercase;">Total</div>
          </td>
        </tr>
      </table>
    </div>
    <div style="height:3px;background:#e4e4f0;"><div style="height:3px;width:{progress_pct}%;background:linear-gradient(90deg,#7c6bff,#34d399);"></div></div>
    <div style="padding:28px 34px;background:#fff;">
      {marco_block}
      {amer_block}
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border-top:1.5px solid #e8e8f2;background:#f7f7fc;">
      <tr>
        <td style="padding:16px 34px;font-family:monospace;font-size:10px;color:#b0b0cc;">Sent automatically · {gen_time_str} · {date_str}</td>
        <td style="padding:16px 34px;text-align:right;"><a href="https://linear.app/platformeq" style="font-family:monospace;font-size:10px;color:#7c6bff;text-decoration:none;">Open Linear ↗</a></td>
      </tr>
    </table>
    <div style="height:4px;background:linear-gradient(90deg,#7c6bff 0%,#34d399 100%);"></div>
  </div>
</div>
</body></html>"""

    return html, f"[{subject_date}] Sweep Report"
