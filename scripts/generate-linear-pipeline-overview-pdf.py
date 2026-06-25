#!/usr/bin/env python3
"""Generate a non-technical executive PDF for the Linear data pipeline."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

OUTPUT = (
    Path(__file__).resolve().parent.parent / "docs" / "linear-data-pipeline-overview.pdf"
)

# Palette
NAVY = (15, 52, 96)
BLUE = (30, 90, 160)
TEAL = (20, 130, 120)
GREEN = (30, 140, 80)
ORANGE = (200, 110, 30)
GREY_DARK = (45, 45, 45)
GREY_MID = (90, 90, 90)
GREY_LIGHT = (150, 150, 150)
WHITE = (255, 255, 255)
BG_SOFT = (248, 250, 252)
BG_BRONZE = (255, 243, 224)
BG_SILVER = (236, 240, 245)
BG_GOLD = (255, 248, 220)
BG_DONE = (232, 248, 238)
BG_TODO = (245, 245, 245)


class PipelinePDF(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self._section = ""

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 11, "F")
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*WHITE)
        self.set_xy(10, 2)
        self.cell(120, 7, "Linear Data Pipeline  |  Executive Overview")
        self.set_xy(130, 2)
        self.cell(70, 7, self._section, align="R")
        self.ln(12)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY_LIGHT)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}  |  PlatformEq tools-gcp / peq-tools", align="C")

    def cover(self) -> None:
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(42)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*WHITE)
        self.multi_cell(0, 12, "Linear Data Pipeline", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 14)
        self.set_text_color(190, 215, 255)
        self.multi_cell(
            0,
            8,
            "Executive Overview\nHow we copy, store, and use Linear data in Google Cloud",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(10)
        self.set_fill_color(*BLUE)
        self.rect(40, self.get_y(), 130, 1, "F")
        self.ln(14)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(220, 235, 255)
        for label, val in [
            ("Prepared for", "Leadership review"),
            ("GCP project", "peq-tools (non-production)"),
            ("Status", "Phase 3 complete - building toward full pipeline"),
            ("Date", "June 2026"),
        ]:
            self.set_x(48)
            self.set_font("Helvetica", "B", 10)
            self.cell(42, 7, label + ":")
            self.set_font("Helvetica", "", 10)
            self.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")
        self.ln(20)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(170, 200, 240)
        self.multi_cell(
            0,
            6,
            "Visual guide - minimal technical jargon",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    def h1(self, num: str, title: str) -> None:
        self._section = title
        self.ln(3)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*NAVY)
        self.multi_cell(0, 8, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLUE)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def h2(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLUE)
        self.multi_cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(0, 5.2, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(0, 5.2, f"  -  {text}", new_x="LMARGIN", new_y="NEXT")

    def callout(self, title: str, text: str, fill: tuple[int, int, int]) -> None:
        self.set_fill_color(*fill)
        self.set_draw_color(*GREY_LIGHT)
        y0 = self.get_y()
        self.rect(10, y0, 190, 18, "DF")
        self.set_xy(14, y0 + 3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*NAVY)
        self.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        self.set_x(14)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(182, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def flow_box(self, x: float, y: float, w: float, h: float, label: str, fill: tuple[int, int, int]) -> None:
        self.set_fill_color(*fill)
        self.set_draw_color(*BLUE)
        self.rect(x, y, w, h, "DF")
        self.set_xy(x + 2, y + h / 2 - 4)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*NAVY)
        self.multi_cell(w - 4, 4.5, label, align="C")

    def arrow_down(self, x: float, y: float, h: float = 8) -> None:
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        self.line(x, y, x, y + h - 2)
        self.line(x, y + h - 2, x - 2, y + h - 5)
        self.line(x, y + h - 2, x + 2, y + h - 5)

    def arrow_right(self, x: float, y: float, w: float = 12) -> None:
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        self.line(x, y, x + w - 2, y)
        self.line(x + w - 2, y, x + w - 5, y - 2)
        self.line(x + w - 2, y, x + w - 5, y + 2)

    def diagram_big_picture(self) -> None:
        self.h2("End-to-end flow (target state)")
        y0 = self.get_y() + 2
        bw, bh = 36, 14
        gap = 8
        labels = [
            ("Linear\n(work tracker)", (255, 230, 230)),
            ("Copy job\n(6 AM)", BG_SOFT),
            ("Archive\n(bronze)", BG_BRONZE),
            ("Clean tables\n(silver)", BG_SILVER),
            ("Report views\n(gold)", BG_GOLD),
            ("Daily email\n(9 AM)", (230, 245, 255)),
        ]
        x = 12
        for i, (label, color) in enumerate(labels):
            self.flow_box(x, y0, bw, bh, label, color)
            if i < len(labels) - 1:
                self.arrow_right(x + bw, y0 + bh / 2, gap + 4)
            x += bw + gap
        self.set_y(y0 + bh + 6)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(*GREY_MID)
        self.multi_cell(
            0,
            5,
            "Think of it like a photocopier (copy job) that files snapshots (archive), "
            "then a librarian sorts them into a catalog (silver), and reports read from "
            "a simple summary shelf (gold).",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(2)

    def diagram_three_layers(self) -> None:
        self.h2("The three storage layers")
        layers = [
            ("BRONZE - Raw archive", "Exact copies as JSON files in cloud storage. "
             "Never deleted - full history for audits.", BG_BRONZE, "Done today"),
            ("SILVER - Master tables", "One current row per issue, user, team, etc. "
             "Updates merge in - no duplicates.", BG_SILVER, "Phase 4"),
            ("GOLD - Report-ready views", "Simple views shaped for emails and dashboards. "
             "Tools only read from here.", BG_GOLD, "Phase 5"),
        ]
        y = self.get_y() + 2
        for title, desc, color, status in layers:
            self.set_fill_color(*color)
            self.rect(10, y, 190, 22, "F")
            self.set_xy(14, y + 3)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*NAVY)
            self.cell(100, 5, title)
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*TEAL if status == "Done today" else ORANGE)
            self.cell(0, 5, status, align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_x(14)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*GREY_DARK)
            self.multi_cell(182, 4.8, desc, new_x="LMARGIN", new_y="NEXT")
            y += 24
        self.set_y(y + 2)

    def diagram_progress(self) -> None:
        self.h2("Project progress")
        phases = [
            ("Phase 1-2", "Platform + daily email", 100, True),
            ("Phase 3", "Copy Linear to cloud archive", 100, True),
            ("Phase 4", "Clean data in BigQuery (silver)", 0, False),
            ("Phase 5", "Reports use database, not Linear API", 0, False),
            ("Phase 6", "Monitoring, retention, production org", 0, False),
        ]
        for name, desc, pct, done in phases:
            y = self.get_y()
            self.set_font("Helvetica", "B", 9.5)
            self.set_text_color(*NAVY)
            self.cell(38, 6, name)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*GREY_DARK)
            self.cell(62, 6, desc)
            bar_x = 112
            self.set_fill_color(*BG_TODO)
            self.rect(bar_x, y + 1, 70, 5, "F")
            if pct > 0:
                self.set_fill_color(*GREEN if done else ORANGE)
                self.rect(bar_x, y + 1, 70 * pct / 100, 5, "F")
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*GREEN if done else GREY_MID)
            self.cell(0, 6, "Done" if done else "Planned", align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(1)
        self.ln(2)

    def diagram_daily_schedule(self) -> None:
        self.h2("Typical weekday schedule (target)")
        y0 = self.get_y() + 4
        self.set_draw_color(*GREY_LIGHT)
        self.line(20, y0 + 20, 190, y0 + 20)
        events = [
            (35, "6:00 AM", "Copy job runs", "Pull overnight\nchanges only"),
            (105, "9:00 AM", "Sweep email", "Already working\ntoday"),
        ]
        for x, time, title, sub in events:
            self.set_fill_color(*BLUE)
            self.ellipse(x - 3, y0 + 17, 6, 6, "F")
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*BLUE)
            self.set_xy(x - 18, y0)
            self.cell(40, 5, time, align="C")
            self.set_xy(x - 22, y0 + 24)
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*NAVY)
            self.cell(48, 5, title, align="C")
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*GREY_MID)
            self.set_xy(x - 22, y0 + 30)
            self.multi_cell(48, 4, sub, align="C")
        self.set_y(y0 + 48)

    def diagram_incremental(self) -> None:
        self.h2('How "only new changes" works (bookmark)')
        y0 = self.get_y() + 2
        boxes = [
            (15, "Last successful\ncopy time", BG_SOFT),
            (75, "Ask Linear:\nwhat changed since?", (230, 240, 255)),
            (135, "Save new files +\nupdate bookmark", BG_BRONZE),
        ]
        for x, label, color in boxes:
            self.flow_box(x, y0, 55, 20, label, color)
        self.arrow_right(70, y0 + 10, 5)
        self.arrow_right(130, y0 + 10, 5)
        self.set_y(y0 + 26)
        self.body(
            "After the first full copy (backfill), daily runs only fetch records that "
            "were updated since the last bookmark - not the entire history every morning."
        )

    def diagram_security(self) -> None:
        self.h2("Where the API key lives")
        y0 = self.get_y() + 2
        self.flow_box(15, y0, 50, 16, "You provide\nAPI key once", (255, 240, 240))
        self.arrow_right(65, y0 + 8, 8)
        self.flow_box(78, y0, 55, 16, "Google Secret\nManager (locked)", (220, 235, 255))
        self.arrow_right(133, y0 + 8, 8)
        self.flow_box(146, y0, 48, 16, "Copy job only\nreads key at run", BG_SOFT)
        self.set_y(y0 + 22)
        self.bullet("Key is never stored in code, email, or spreadsheets")
        self.bullet("Separate secret for the copy job vs. the email job (planned split)")
        self.bullet("Access is logged; only approved cloud accounts can read secrets")
        self.ln(1)


def build_pdf() -> None:
    pdf = PipelinePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=16)

    # Cover
    pdf.add_page()
    pdf.cover()

    # TOC
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for num, title in [
        ("1", "Executive summary"),
        ("2", "Why we are building this"),
        ("3", "How the pipeline works (visual)"),
        ("4", "What is done vs. what is next"),
        ("5", "Daily schedule"),
        ("6", "Security & the API key"),
        ("7", "Audit & record-keeping"),
        ("8", "What we need to go live on real data"),
        ("9", "FAQ"),
    ]:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*GREY_DARK)
        pdf.cell(12, 7, num)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    # 1 Executive summary
    pdf.add_page()
    pdf.h1("1", "Executive summary")
    pdf.body(
        "We are building a reliable copy of our Linear (project management) data inside "
        "Google Cloud. Once complete, reports and tools will read from our own database "
        "instead of calling Linear directly every time."
    )
    pdf.callout(
        "Bottom line",
        "Phase 3 is complete: we can copy Linear data into secure cloud storage on demand. "
        "The daily sweep email already works on weekdays at 9 AM. Next steps turn that "
        "archive into queryable tables and point the email at those tables.",
        BG_DONE,
    )
    pdf.h2("In one sentence")
    pdf.body(
        "Linear remains the source of truth; Google Cloud becomes our durable, auditable copy "
        "that powers internal reporting."
    )

    # 2 Why
    pdf.h1("2", "Why we are building this")
    pdf.bullet("Auditability - prove what we knew on any past date (immutable archive)")
    pdf.bullet("Reliability - reports do not break if Linear is slow or rate-limits us")
    pdf.bullet("Speed - query our database instead of re-downloading history daily")
    pdf.bullet("Foundation - same pattern works for Epic and other sources later")
    pdf.bullet("Security - credentials in Google Secret Manager, not in scripts or inboxes")

    # 3 How it works
    pdf.add_page()
    pdf.h1("3", "How the pipeline works (visual)")
    pdf.diagram_big_picture()
    pdf.diagram_three_layers()
    pdf.diagram_incremental()

    # 4 Progress
    pdf.add_page()
    pdf.h1("4", "What is done vs. what is next")
    pdf.diagram_progress()
    pdf.h2("Completed (validated)")
    pdf.bullet("Cloud infrastructure in peq-tools (storage, database shells, jobs)")
    pdf.bullet("linear-ingest copy job - local and cloud tested")
    pdf.bullet("Full backfill of test Linear workspace into cloud archive")
    pdf.bullet("Bookmark file tracks last copy time per data type")
    pdf.bullet("Weekday 9 AM sweep email sending successfully")
    pdf.h2("Not started yet")
    pdf.bullet("Silver tables - cleaned master data in BigQuery")
    pdf.bullet("Gold views - report-shaped data for tools")
    pdf.bullet("Sweep email reading from database instead of Linear API")
    pdf.bullet("Automatic 6 AM daily copy schedule")
    pdf.bullet("Production Linear organization backfill")

    # 5 Schedule
    pdf.h1("5", "Daily schedule")
    pdf.body(
        "Today only the 9 AM email is on a timer. The 6 AM copy job will be scheduled "
        "after silver/gold layers are built - so data is fresh before the email goes out."
    )
    pdf.diagram_daily_schedule()

    # 6 Security
    pdf.add_page()
    pdf.h1("6", "Security & the API key")
    pdf.body(
        "To copy production Linear data we need a read API key from the real organization. "
        "It will be stored once in Google Secret Manager and used only by the automated copy job."
    )
    pdf.diagram_security()
    pdf.h2("What the key is used for")
    pdf.bullet("Read-only copy of issues, users, teams, comments, and related records")
    pdf.bullet("Not shared with the email job once we finish Phase 5 (email uses database only)")
    pdf.h2("What we are NOT doing")
    pdf.bullet("Storing the key in GitHub, code, or Terraform")
    pdf.bullet("Giving every employee direct access to the key")
    pdf.bullet("Writing changes back into Linear")

    # 7 Audit
    pdf.h1("7", "Audit & record-keeping")
    pdf.body(
        "Every copy run creates a new dated folder in cloud storage. We do not overwrite "
        "historical snapshots - we add new ones. That supports questions like "
        '"What did Linear show us on March 3?"'
    )
    pdf.h2("What is logged today")
    pdf.bullet("Each copy run: timestamp, record counts, success/failure per data type")
    pdf.bullet("Cloud job execution logs in Google Cloud Logging")
    pdf.bullet("Secret access audit trail for API key reads")
    pdf.h2("Planned improvements")
    pdf.bullet("Retention policy (how long to keep raw archives)")
    pdf.bullet("Alerts if copy or email jobs fail")
    pdf.bullet("Master tables in BigQuery with merge history")

    # 8 What we need
    pdf.h1("8", "What we need to go live on real data")
    pdf.body("To move from the small test workspace to production Linear:")
    pdf.bullet("Production Linear API key (read access) added to ingest secret")
    pdf.bullet("One-time full copy (backfill) of the real organization - may take longer than test")
    pdf.bullet("Complete Phase 4-5 before reports depend on database copy")
    pdf.bullet("Confirm which teams/issues are in scope for reporting")
    pdf.callout(
        "Recommendation",
        "Provide the production API key when ready for backfill. We can run a dry-run first "
        "(connectivity check, no storage changes) before the full copy.",
        (255, 252, 230),
    )

    # 9 FAQ
    pdf.add_page()
    pdf.h1("9", "FAQ")
    faqs = [
        (
            "Is the daily email already working?",
            "Yes - weekday 9 AM emails are sending. They still call Linear directly today; "
            "the database pipeline will replace that later.",
        ),
        (
            "Is data copying automatically every morning?",
            "Not yet - copy runs on demand. A 6 AM schedule comes after silver/gold are built.",
        ),
        (
            "Will we have a big -bronze database- in BigQuery?",
            "The raw archive lives in cloud file storage (bronze). BigQuery will hold cleaned "
            "silver tables and gold report views - not necessarily another bronze copy.",
        ),
        (
            "Does incremental copy re-download everything?",
            "No - after the first full copy, daily runs use a bookmark to fetch only changes.",
        ),
        (
            "What if we add Epic or other tools later?",
            "Same pattern: separate copy job, archive, and silver/gold per source. "
            "Cross-tool reports join in a shared analytics layer.",
        ),
        (
            "How much will this cost?",
            "At our scale, storage and queries in Google Cloud are expected to be low "
            "(typically dollars per month, not thousands) for Linear-sized data.",
        ),
    ]
    for q, a in faqs:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*NAVY)
        pdf.multi_cell(0, 5.5, f"Q: {q}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(0, 5, f"A: {a}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
