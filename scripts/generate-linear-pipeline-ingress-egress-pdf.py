#!/usr/bin/env python3
"""Generate ingress/egress PDF for the Linear data pipeline (executive audience)."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "linear-data-pipeline-ingress-egress.pdf"
)

NAVY = (15, 52, 96)
BLUE = (30, 90, 160)
GREEN = (30, 140, 80)
RED = (180, 60, 50)
ORANGE = (200, 110, 30)
GREY_DARK = (45, 45, 45)
GREY_MID = (90, 90, 90)
GREY_LIGHT = (150, 150, 150)
WHITE = (255, 255, 255)
BG_IN = (232, 242, 255)
BG_OUT = (255, 236, 230)
BG_JOB = (248, 250, 252)
BG_OK = (232, 248, 238)
BG_WARN = (255, 248, 230)
BG_NONE = (245, 245, 245)


class FlowPDF(FPDF):
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
        self.cell(120, 7, "Linear Pipeline  |  Ingress & Egress")
        self.set_xy(130, 2)
        self.cell(70, 7, self._section, align="R")
        self.ln(12)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY_LIGHT)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}  |  peq-tools / tools-gcp", align="C")

    def cover(self) -> None:
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(50)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*WHITE)
        self.multi_cell(0, 11, "Data Ingress & Egress", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 13)
        self.set_text_color(190, 215, 255)
        self.multi_cell(
            0,
            7,
            "Where data enters and leaves each part\nof the Linear pipeline (today vs target)",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(12)
        self.set_fill_color(*BLUE)
        self.rect(35, self.get_y(), 140, 1, "F")
        self.ln(16)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(220, 235, 255)
        for label, val in [
            ("GCP project", "peq-tools"),
            ("Focus", "What the cron jobs actually touch"),
            ("Date", "June 2026"),
        ]:
            self.set_x(50)
            self.set_font("Helvetica", "B", 10)
            self.cell(36, 7, label + ":")
            self.set_font("Helvetica", "", 10)
            self.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")

    def h1(self, num: str, title: str) -> None:
        self._section = title
        self.ln(2)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*NAVY)
        self.multi_cell(0, 8, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLUE)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def h2(self, title: str) -> None:
        self.ln(1)
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
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(0, 5, f"  -  {text}", new_x="LMARGIN", new_y="NEXT")

    def callout(self, title: str, text: str, fill: tuple[int, int, int]) -> None:
        y0 = self.get_y()
        self.set_fill_color(*fill)
        self.rect(10, y0, 190, 20, "F")
        self.set_xy(14, y0 + 3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*NAVY)
        self.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        self.set_x(14)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(182, 4.8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def box(self, x: float, y: float, w: float, h: float, title: str, sub: str, fill: tuple[int, int, int]) -> None:
        self.set_fill_color(*fill)
        self.set_draw_color(*BLUE)
        self.rect(x, y, w, h, "DF")
        self.set_xy(x + 2, y + 3)
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*NAVY)
        self.multi_cell(w - 4, 4, title, align="C")
        self.set_xy(x + 2, y + h - 9)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*GREY_MID)
        self.multi_cell(w - 4, 3.5, sub, align="C")

    def arrow_r(self, x: float, y: float, w: float, label: str = "") -> None:
        self.set_draw_color(*BLUE)
        self.set_line_width(0.35)
        self.line(x, y, x + w - 3, y)
        self.line(x + w - 3, y, x + w - 6, y - 1.5)
        self.line(x + w - 3, y, x + w - 6, y + 1.5)
        if label:
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(*TEAL if hasattr(self, "_teal") else BLUE)
            self.set_xy(x + 2, y - 5)
            self.cell(w - 4, 3, label, align="C")

    def arrow_d(self, x: float, y: float, h: float) -> None:
        self.set_draw_color(*BLUE)
        self.line(x, y, x, y + h - 3)
        self.line(x, y + h - 3, x - 1.5, y + h - 6)
        self.line(x, y + h - 3, x + 1.5, y + h - 6)

    def legend_in_out(self) -> None:
        self.box(12, self.get_y(), 42, 12, "INGRESS", "data coming IN", BG_IN)
        self.box(58, self.get_y(), 42, 12, "EGRESS", "data going OUT", BG_OUT)
        self.box(104, self.get_y(), 48, 12, "JOB", "runs in Cloud Run", BG_JOB)
        self.box(156, self.get_y(), 44, 12, "CRON", "Cloud Scheduler", (230, 230, 250))
        self.ln(16)

    def flow_row(
        self,
        y: float,
        ingress: list[tuple[str, str]],
        job_title: str,
        job_sub: str,
        egress: list[tuple[str, str]],
        cron: str = "",
    ) -> float:
        """Draw one horizontal ingress -> job -> egress strip. Returns bottom y."""
        ix = 10
        for title, sub in ingress:
            self.box(ix, y, 38, 22, title, sub, BG_IN)
            self.arrow_r(ix + 38, y + 11, 8)
            ix += 46
        self.box(ix, y, 44, 22, job_title, job_sub, BG_JOB)
        jx = ix + 44
        ex = jx
        for i, (title, sub) in enumerate(egress):
            self.arrow_r(ex, y + 11, 8)
            ex += 8
            self.box(ex, y, 38, 22, title, sub, BG_OUT)
            ex += 46
        if cron:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*ORANGE)
            self.set_xy(ix, y - 6)
            self.cell(44, 4, cron, align="C")
        return y + 26

    def ie_table(self, rows: list[tuple[str, str, str, str]]) -> None:
        """Headers: component, trigger, ingress, egress."""
        col_w = [38, 28, 62, 62]
        headers = ["Component", "Trigger", "Ingress (in)", "Egress (out)"]
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 8)
        x = 10
        for w, h in zip(col_w, headers, strict=True):
            self.set_xy(x, self.get_y())
            self.cell(w, 6, h, border=1, fill=True)
            x += w
        self.ln()
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*GREY_DARK)
        for row in rows:
            x = 10
            y = self.get_y()
            max_h = 6
            for i, (w, cell) in enumerate(zip(col_w, row, strict=True)):
                self.set_xy(x, y)
                self.multi_cell(w, 4.5, cell, border=1)
                max_h = max(max_h, self.get_y() - y)
                x += w
            self.set_y(y + max_h)
        self.ln(3)


TEAL = (20, 130, 120)


def build_pdf() -> None:
    pdf = FlowPDF()
    pdf._teal = TEAL  # type: ignore[attr-defined]
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=14)

    pdf.add_page()
    pdf.cover()

    # TOC
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 9, "Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    for n, t in [
        ("1", "What ingress and egress mean"),
        ("2", "Quick answer: what does cron do today?"),
        ("3", "TODAY: 9 AM email job (live)"),
        ("4", "TODAY: Copy job (built, manual only)"),
        ("5", "TODAY: BigQuery (not connected yet)"),
        ("6", "TARGET: full pipeline with two crons"),
        ("7", "Side-by-side comparison table"),
        ("8", "Where to study in the repo"),
    ]:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GREY_DARK)
        pdf.cell(10, 6, n)
        pdf.cell(0, 6, t, new_x="LMARGIN", new_y="NEXT")

    # 1 Definitions
    pdf.add_page()
    pdf.h1("1", "What ingress and egress mean")
    pdf.body(
        "Every piece of the pipeline has data flowing IN and data flowing OUT. "
        "Leaders often ask for this map so they can see what each job actually touches."
    )
    pdf.legend_in_out()
    pdf.h2("Simple definitions")
    pdf.bullet("Ingress = data entering a component (reads, downloads, fetches)")
    pdf.bullet("Egress = data leaving a component (writes, uploads, sends)")
    pdf.bullet("A job sits in the middle: it pulls data in, transforms it, pushes data out")
    pdf.callout(
        "Key idea",
        "The pipeline diagram shows boxes. This document shows the ARROWS - "
        "what crosses each boundary and over which channel (API, email, files, database).",
        BG_WARN,
    )

    # 2 Cron answer
    pdf.h1("2", "Quick answer: what does cron do today?")
    pdf.callout(
        "Today: only ONE cron job",
        "Cloud Scheduler runs daily-sweep-report at 9:00 AM Eastern, Mon-Fri. "
        "It sends the sweep email. It does NOT run the Linear data copy.",
        BG_OK,
    )
    pdf.h2("Scheduled vs manual today")
    pdf.ie_table(
        [
            ("daily-sweep-report", "CRON 9 AM", "Secret Mgr + Linear API", "Gmail to inbox"),
            ("linear-ingest (copy)", "Manual only", "Secret Mgr + Linear API", "GCS bronze files"),
            ("BigQuery silver/gold", "N/A", "Nothing yet", "Nothing yet"),
        ]
    )

    # 3 Email job today
    pdf.add_page()
    pdf.h1("3", "TODAY: 9 AM email job (live)")
    pdf.body(
        "Job name: daily-sweep-report. Runs on Cloud Run in GCP project peq-tools. "
        "Currently uses a test Linear workspace via the API - not the gold database layer."
    )
    y = pdf.get_y() + 4
    pdf.flow_row(
        y,
        ingress=[
            ("Secret\nManager", "API key +\nGmail creds"),
            ("Linear API", "Issue data\n(HTTPS)"),
        ],
        job_title="Email job",
        job_sub="Build HTML\nreport",
        egress=[("Gmail", "SMTP send"), ("Your inbox", "HTML email")],
        cron="CRON 9 AM ET",
    )
    pdf.set_y(y + 30)
    pdf.h2("Ingress detail (what comes IN)")
    pdf.bullet("peq-tools-daily-sweep-report-config: Linear API key, Gmail address/password, recipients")
    pdf.bullet("Linear GraphQL API: issues matching yesterday's sweep window")
    pdf.h2("Egress detail (what goes OUT)")
    pdf.bullet("One HTML email per run via Gmail SMTP (ports 465/587 from cloud - works)")
    pdf.h2("What this job does NOT touch today")
    pdf.bullet("GCS bucket peq-tools-linear-data (bronze archive)")
    pdf.bullet("BigQuery linear_silver or linear_gold")
    pdf.bullet("peq-tools-linear-ingest-config secret")

    # 4 Copy job today
    pdf.add_page()
    pdf.h1("4", "TODAY: Copy job (built, manual only)")
    pdf.body(
        "Job name: linear-ingest. Same Cloud Run platform, different command. "
        "Validated locally and in cloud - but NO Cloud Scheduler attached yet."
    )
    y = pdf.get_y() + 4
    pdf.flow_row(
        y,
        ingress=[
            ("Secret\nManager", "ingest API key"),
            ("Linear API", "10 entity types\n(HTTPS)"),
        ],
        job_title="Copy job",
        job_sub="Backfill or\nincremental",
        egress=[
            ("GCS bronze", "JSON pages"),
            ("Watermarks", "bookmark file"),
        ],
        cron="MANUAL trigger",
    )
    pdf.set_y(y + 30)
    pdf.h2("Ingress detail")
    pdf.bullet("peq-tools-linear-ingest-config: Linear API key (read-only)")
    pdf.bullet("Linear API: organization, teams, issues, users, comments, etc.")
    pdf.h2("Egress detail")
    pdf.bullet("gs://peq-tools-linear-data/bronze/backfill|daily/run_.../page_*.json")
    pdf.bullet("gs://peq-tools-linear-data/state/watermarks.json (updated each successful run)")
    pdf.bullet("Per-run summary.json with record counts and status")
    pdf.h2("Incremental / watermark behavior")
    pdf.bullet("backfill = full history once; incremental = only records changed since bookmark")
    pdf.bullet("Reference entities (teams, labels) still full-snapshot each run")

    # 5 BQ not connected
    pdf.h1("5", "TODAY: BigQuery (not connected yet)")
    pdf.body(
        "Terraform created datasets linear_bronze, linear_silver, linear_gold. "
        "They are empty shells. No job reads or writes them yet."
    )
    y = pdf.get_y() + 2
    pdf.box(30, y, 150, 28, "BigQuery datasets", "No ingress. No egress. Phase 4-5.", BG_NONE)
    pdf.set_y(y + 34)

    # 6 Target
    pdf.add_page()
    pdf.h1("6", "TARGET: full pipeline with two crons")
    pdf.body("When complete, two scheduled jobs run each weekday morning in order:")
    pdf.ln(2)
    y = pdf.get_y()
    # 6 AM row
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*ORANGE)
    pdf.cell(0, 5, "~6:00 AM - linear-ingest (CRON - planned)", new_x="LMARGIN", new_y="NEXT")
    pdf.flow_row(
        y + 6,
        ingress=[("Secret Mgr", "ingest key"), ("Linear API", "delta only")],
        job_title="Copy job",
        job_sub="incremental",
        egress=[("GCS", "bronze"), ("BigQuery", "silver MERGE")],
    )
    pdf.arrow_d(105, y + 34, 10)
    y2 = y + 48
    pdf.set_xy(10, y2 - 4)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*ORANGE)
    pdf.cell(0, 5, "~9:00 AM - daily-sweep-report (CRON - live today, changes in Phase 5)", new_x="LMARGIN", new_y="NEXT")
    pdf.flow_row(
        y2 + 6,
        ingress=[("Secret Mgr", "Gmail only"), ("BigQuery gold", "SQL read")],
        job_title="Email job",
        job_sub="no Linear API",
        egress=[("Gmail", "send"), ("Inbox", "report")],
    )
    pdf.set_y(y2 + 42)
    pdf.callout(
        "Main change in Phase 5",
        "The 9 AM email stops calling Linear. It only reads gold views in BigQuery. "
        "Linear API is used only by the 6 AM copy job.",
        BG_OK,
    )

    # 7 Comparison table
    pdf.add_page()
    pdf.h1("7", "Side-by-side comparison")
    pdf.h2("Today vs target - ingress and egress per job")
    pdf.ie_table(
        [
            (
                "9 AM email (today)",
                "Cron",
                "IN: Secret Mgr, Linear API",
                "OUT: Gmail email",
            ),
            (
                "9 AM email (target)",
                "Cron",
                "IN: Secret Mgr, BQ gold",
                "OUT: Gmail email",
            ),
            (
                "Copy job (today)",
                "Manual",
                "IN: Secret Mgr, Linear API",
                "OUT: GCS bronze only",
            ),
            (
                "Copy job (target)",
                "Cron ~6 AM",
                "IN: Secret Mgr, Linear API",
                "OUT: GCS + BQ silver",
            ),
            (
                "BigQuery gold",
                "Views",
                "IN: silver tables",
                "OUT: read by email job",
            ),
        ]
    )
    pdf.h2("Network direction summary (external systems)")
    pdf.bullet("Linear API: ingress TO our jobs only (read today; write maybe later)")
    pdf.bullet("Gmail: egress FROM email job only")
    pdf.bullet("Secret Manager: ingress TO jobs (credentials never in code)")
    pdf.bullet("GCS + BigQuery: internal GCP storage between our jobs")

    # 8 Study guide
    pdf.h1("8", "Where to study in the repo")
    pdf.ie_table(
        [
            ("9 AM cron config", "Terraform", "cloud_run_jobs.tf", "scheduler block"),
            ("Email job code", "Python", "src/jobs/daily-sweep-report/", "linear.py, gmail.py"),
            ("Copy job code", "Python", "src/jobs/linear-ingest/", "extract.py, gcs.py"),
            ("Bronze files", "GCS", "gs://peq-tools-linear-data/bronze/", "JSON archive"),
            ("Architecture", "Docs", "docs/ARCHITECTURE.md", "full design"),
        ]
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
