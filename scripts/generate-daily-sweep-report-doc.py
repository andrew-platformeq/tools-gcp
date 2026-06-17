#!/usr/bin/env python3
"""Generate comprehensive documentation PDF for the daily-sweep-report job."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "daily-sweep-report-guide.pdf"
)

BLUE_DARK = (15, 52, 96)
BLUE_MID = (30, 90, 160)
GREY_DARK = (40, 40, 40)
GREY_MID = (80, 80, 80)
GREY_LIGHT = (130, 130, 130)
WHITE = (255, 255, 255)
BG_CODE = (245, 247, 250)
BG_NOTE = (255, 253, 235)
BG_TIP = (240, 255, 245)
ACCENT_GREEN = (30, 140, 80)
ACCENT_ORANGE = (200, 100, 30)


class GuidePDF(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self._section = ""

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_fill_color(*BLUE_DARK)
        self.rect(0, 0, 210, 11, "F")
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*WHITE)
        self.set_xy(10, 2)
        self.cell(120, 7, "daily-sweep-report  --  Technical Guide")
        self.set_xy(130, 2)
        self.cell(70, 7, self._section, align="R")
        self.ln(12)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY_LIGHT)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}  |  tools-gcp / peq-tools", align="C")

    def cover(self) -> None:
        self.set_fill_color(*BLUE_DARK)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(48)
        self.set_font("Helvetica", "B", 30)
        self.set_text_color(*WHITE)
        self.multi_cell(0, 12, "daily-sweep-report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 15)
        self.set_text_color(180, 210, 255)
        self.multi_cell(
            0, 8,
            "Technical Guide & GCP Hosting Reference",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(8)
        self.set_fill_color(*BLUE_MID)
        self.rect(35, self.get_y(), 140, 1, "F")
        self.ln(10)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(210, 230, 255)
        self.multi_cell(
            0, 6,
            "How the daily Linear sweep summary email works,\n"
            "how it uses GCP Secret Manager, and how it will\n"
            "be scheduled and hosted on Google Cloud.",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(18)
        meta = [
            ("Repository", "andrew-platformeq/tools-gcp"),
            ("GCP project", "peq-tools"),
            ("Job folder", "src/jobs/daily-sweep-report/"),
            ("CLI command", "tools-daily-sweep-report"),
            ("Generated", "June 2026"),
        ]
        for label, val in meta:
            self.set_x(42)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(160, 200, 255)
            self.cell(38, 7, label + ":")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*WHITE)
            self.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")

    def h1(self, num: str, title: str) -> None:
        self._section = title
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*BLUE_DARK)
        self.multi_cell(0, 8, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLUE_MID)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def h2(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLUE_MID)
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

    def code(self, text: str) -> None:
        self.set_font("Courier", "", 8.2)
        self.set_text_color(20, 20, 20)
        self.set_fill_color(*BG_CODE)
        for line in text.strip().splitlines():
            self.cell(0, 4.6, f"  {line}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

    def note(self, text: str) -> None:
        self.set_fill_color(*BG_NOTE)
        y = self.get_y()
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*GREY_MID)
        self.multi_cell(0, 5, f"  Note: {text}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        _ = y

    def tip(self, text: str) -> None:
        self.set_fill_color(*BG_TIP)
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*ACCENT_GREEN)
        self.multi_cell(0, 5, f"  Tip: {text}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def table_row(self, col1: str, col2: str, bold_left: bool = True) -> None:
        x, y = self.get_x(), self.get_y()
        if bold_left:
            self.set_font("Helvetica", "B", 9)
        else:
            self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(58, 5.2, col1)
        self.set_xy(x + 58, y)
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 5.2, col2, new_x="LMARGIN", new_y="NEXT")

    def diagram(self, text: str) -> None:
        self.set_font("Courier", "", 8)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(248, 250, 252)
        for line in text.strip().splitlines():
            self.cell(0, 4.4, f"  {line}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)


def build_pdf() -> None:
    pdf = GuidePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.cover()

    # TOC
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*BLUE_DARK)
    pdf.cell(0, 10, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    toc = [
        ("1", "Executive Summary"),
        ("2", "What the Job Does"),
        ("3", "Repository Layout & Module Reference"),
        ("4", "End-to-End Execution Flow"),
        ("5", "Date & Timezone Logic"),
        ("6", "Linear Integration"),
        ("7", "Issue Matching & Report Statuses"),
        ("8", "HTML Email Report"),
        ("9", "Gmail Delivery"),
        ("10", "Configuration & Secrets"),
        ("11", "GCP Integration (Detailed)"),
        ("12", "Hosting on GCP: Current vs Target"),
        ("13", "Cloud Run Job + Scheduler Architecture"),
        ("14", "IAM, Identity & Security Model"),
        ("15", "Local Development & Testing"),
        ("16", "Migration from GitHub Actions"),
        ("17", "Operations, Monitoring & Troubleshooting"),
        ("18", "Future Jobs in tools-gcp"),
    ]
    for num, title in toc:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*GREY_DARK)
        pdf.cell(12, 7, num)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    # 1 Executive Summary
    pdf.add_page()
    pdf.h1("1", "Executive Summary")
    pdf.body(
        "daily-sweep-report is a batch job in the tools-gcp repository. Every weekday "
        "morning it emails a summary of four recurring Linear sweep tasks for Team Mekhael: "
        "Beginning of Day and End of Day sweeps for Marco Durante and Amer Roufail."
    )
    pdf.body(
        "The job replaces an earlier GitHub Actions workflow that ran inline Python with "
        "credentials stored in GitHub Secrets. The new design stores secrets in GCP Secret "
        "Manager, runs as a CLI command (tools-daily-sweep-report), and is designed to be "
        "hosted on GCP via Cloud Run Jobs triggered by Cloud Scheduler."
    )
    pdf.h2("Key facts")
    pdf.table_row("Trigger (target)", "Mon-Fri ~9:00 AM America/New_York")
    pdf.table_row("Report window", "Previous business day (Fri on Monday)")
    pdf.table_row("Data source", "Linear GraphQL API")
    pdf.table_row("Output", "HTML email via Gmail SMTP")
    pdf.table_row("Secret container", "peq-tools-daily-sweep-report-config")
    pdf.table_row("Runtime identity (GCP)", "tools-gcp-run@peq-tools.iam.gserviceaccount.com")
    pdf.table_row("CLI entry point", "tools-daily-sweep-report")

    # 2 What the job does
    pdf.h1("2", "What the Job Does")
    pdf.body(
        "Operations teams use recurring Linear issues titled 'Beginning of Day Sweep' and "
        "'End of Day Sweep'. Each team member creates and completes these issues daily. "
        "Managers need a single email showing whether each expected sweep was created, "
        "completed, or missing for the prior day."
    )
    pdf.h2("Watched issue slots (4 total)")
    pdf.bullet("Beginning of Day Sweep  --  Marco Durante")
    pdf.bullet("End of Day Sweep        --  Marco Durante")
    pdf.bullet("Beginning of Day Sweep  --  Amer Roufail")
    pdf.bullet("End of Day Sweep        --  Amer Roufail")
    pdf.note(
        "Titles and assignee names must match Linear exactly (case-insensitive match at runtime)."
    )
    pdf.h2("Three possible states per slot")
    pdf.table_row("Done", "Issue exists and state.type == 'completed'")
    pdf.table_row("Pending", "Issue exists but not completed")
    pdf.table_row("Missing", "No matching issue was created that day")

    # 3 Layout
    pdf.add_page()
    pdf.h1("3", "Repository Layout & Module Reference")
    pdf.body(
        "tools-gcp is structured for many jobs. Shared platform code lives in src/tools/. "
        "Each job gets its own folder under src/jobs/ with kebab-case naming."
    )
    pdf.code(
        """src/
  tools/                          Shared: config, Secret Manager, FastAPI app
  jobs/
    README.md                       Conventions for adding future jobs
    daily-sweep-report/             This job (kebab-case folder)
      config.py                     Watched issues, env settings, secret schema
      secrets.py                    Load JSON credentials from Secret Manager
      dates.py                      Report date window (America/New_York)
      linear.py                     GraphQL fetch + issue matching
      report.py                     HTML email builder
      gmail.py                      SMTP send via Gmail
      main.py                       CLI entry point (run orchestration)"""
    )
    pdf.h2("Module responsibilities")
    pdf.table_row("config.py", "WATCHED_ISSUES list; JobSettings from env; ReportSecrets schema")
    pdf.table_row("secrets.py", "Calls tools.secrets.get_secret(); parses JSON")
    pdf.table_row("dates.py", "yesterday_range_utc() with Mon->Fri rule")
    pdf.table_row("linear.py", "POST to api.linear.app/graphql; match_issues()")
    pdf.table_row("report.py", "build_email() -- HTML template + summary stats")
    pdf.table_row("gmail.py", "send_report_email() via smtp.gmail.com:465")
    pdf.table_row("main.py", "run() pipeline; argparse --dry-run")
    pdf.body(
        "Python imports use daily_sweep_report (snake_case) mapped to the kebab-case folder "
        "via pyproject.toml [tool.setuptools.package-dir]. Future jobs follow the same pattern."
    )

    # 4 Flow
    pdf.add_page()
    pdf.h1("4", "End-to-End Execution Flow")
    pdf.diagram(
        """  START (tools-daily-sweep-report)
    |
    v
  Load JobSettings from env (TOOLS_* vars)
    |
    v
  Load ReportSecrets from Secret Manager (JSON)
    |-- skip if TOOLS_SKIP_GCP=1 (tests / dry-run)
    v
  Compute report date window (dates.yesterday_range_utc)
    |
    v
  Fetch Linear issues created in that window (linear.fetch_issues)
    |-- filter: title in [BOD Sweep, EOD Sweep]
    v
  Match 4 watched slots to fetched nodes (linear.match_issues)
    |
    v
  Build HTML + subject (report.build_email)
    |
    v
  If dry_run or skip_gcp --> log and exit 0
    |
    v
  Send email via Gmail SMTP (gmail.send_report_email)
    |
    v
  END (exit 0)"""
    )
    pdf.h2("Step-by-step detail")
    pdf.body(
        "1. main.py parses --dry-run and configures logging."
    )
    pdf.body(
        "2. load_report_secrets() reads peq-tools-daily-sweep-report-config from Secret "
        "Manager using Application Default Credentials (ADC). The secret value is JSON with "
        "gmail_address, gmail_app_password, send_to, and linear_api_key."
    )
    pdf.body(
        "3. yesterday_range_utc() determines which calendar day the report covers and "
        "returns UTC ISO timestamps for the Linear createdAt filter."
    )
    pdf.body(
        "4. fetch_issues() queries Linear for all sweep-titled issues created in that window."
    )
    pdf.body(
        "5. match_issues() pairs each of the 4 watched slots with at most one Linear issue "
        "by title + assignee name."
    )
    pdf.body(
        "6. build_email() renders the HTML report with per-person sections, status badges, "
        "notes (description minus checklist lines), and summary counts."
    )
    pdf.body(
        "7. send_report_email() connects to Gmail on port 465 (SSL), authenticates with "
        "the app password, and sends to send_to."
    )

    # 5 Dates
    pdf.h1("5", "Date & Timezone Logic")
    pdf.body(
        "All report dates use ZoneInfo('America/New_York'). This handles EST/EDT automatically "
        "unlike a fixed UTC-5 offset."
    )
    pdf.h2("Which day does the report cover?")
    pdf.table_row("Tuesday run", "Monday's sweeps")
    pdf.table_row("Wednesday run", "Tuesday's sweeps")
    pdf.table_row("Monday run", "Friday's sweeps (3 days back, skips weekend)")
    pdf.body(
        "The job runs on weekdays and reports on the previous business day. On Monday, "
        "days_back = 3 so the report covers Friday rather than Sunday."
    )
    pdf.h2("UTC conversion for Linear")
    pdf.body(
        "Linear filters use createdAt with gte/lte in UTC ISO format (e.g. "
        "2026-06-12T04:00:00Z). The local day 00:00:00-23:59:59 America/New_York is "
        "converted to UTC before the API call."
    )
    pdf.code(
        """# Example: report for Friday June 12, 2026 (ET)
start_utc = "2026-06-12T04:00:00Z"   # midnight ET in summer (EDT)
end_utc   = "2026-06-13T03:59:59Z"   # end of day ET"""
    )

    # 6 Linear
    pdf.add_page()
    pdf.h1("6", "Linear Integration")
    pdf.body(
        "The job uses Linear's GraphQL API at https://api.linear.app/graphql. "
        "Authentication is the API key passed in the Authorization header (no Bearer prefix)."
    )
    pdf.h2("GraphQL query")
    pdf.body(
        "Issues are fetched with a filter on createdAt (gte/lte) and title (in list). "
        "Up to 50 nodes are returned. Fields used: identifier, title, description, "
        "completedAt, assignee.name, state.type, url."
    )
    pdf.code(
        """filter: {
  createdAt: { gte: "<start_utc>", lte: "<end_utc>" },
  title: { in: ["Beginning of Day Sweep", "End of Day Sweep"] }
}"""
    )
    pdf.h2("Why createdAt, not completedAt?")
    pdf.body(
        "The report tracks whether sweeps were created for the day and whether they were "
        "marked Done. Missing means no issue was created at all. Pending means created but "
        "state.type != completed. Done uses completedAt for the timestamp display."
    )
    pdf.h2("Error handling")
    pdf.bullet("HTTP errors raise RuntimeError with response body")
    pdf.bullet("GraphQL errors array in response raises RuntimeError")
    pdf.bullet("30-second timeout on the HTTP request")

    # 7 Matching
    pdf.h1("7", "Issue Matching & Report Statuses")
    pdf.body(
        "match_issues() iterates WATCHED_ISSUES in order. For each slot it finds the first "
        "node where title matches (case-insensitive) AND assignee.name matches (case-insensitive)."
    )
    pdf.h2("Description / notes extraction")
    pdf.body(
        "Linear issue descriptions often contain markdown checklists (- [ ] / - [x]). "
        "_extract_notes() strips checklist lines and empty lines, joining remaining text "
        "as the note shown in Done rows."
    )
    pdf.h2("Email summary header counts")
    pdf.table_row("Done", "Issues with state.type == completed")
    pdf.table_row("Pending", "Issues exist but not completed")
    pdf.table_row("Missing", "No issue matched the slot")
    pdf.table_row("Total", "Always 4 (one per watched slot)")

    # 8 HTML
    pdf.add_page()
    pdf.h1("8", "HTML Email Report")
    pdf.body(
        "report.py builds a self-contained HTML email (inline CSS, no external stylesheets "
        "except email-client-safe patterns). Layout:"
    )
    pdf.bullet("Dark header with date, team label, generation time")
    pdf.bullet("Summary stat cards: Done / Pending / Missing / Total")
    pdf.bullet("Progress bar (done/total percentage)")
    pdf.bullet("Marco Durante section -- 2 issue rows")
    pdf.bullet("Amer Roufail section -- 2 issue rows")
    pdf.bullet("Footer with timestamp and link to linear.app/platformeq")
    pdf.body(
        "Subject line format: [Jun 12, 2026] Sweep Report"
    )
    pdf.note(
        "Special characters in user notes are embedded in HTML without escaping in v1. "
        "Trusted internal content only."
    )

    # 9 Gmail
    pdf.h1("9", "Gmail Delivery")
    pdf.body(
        "Email is sent via Gmail SMTP (smtp.gmail.com, port 465, SMTP_SSL). The sending "
        "account uses a Gmail App Password (not the regular account password). App passwords "
        "require 2FA on the Google account."
    )
    pdf.table_row("From", "gmail_address (secret)")
    pdf.table_row("To", "send_to (secret)")
    pdf.table_row("Format", "multipart/alternative with text/html part")
    pdf.tip(
        "Store the app password only in Secret Manager. Rotate by adding a new secret version."
    )

    # 10 Config & secrets
    pdf.add_page()
    pdf.h1("10", "Configuration & Secrets")
    pdf.h2("Non-secret environment variables")
    pdf.table_row("TOOLS_GCP_PROJECT", "peq-tools (default)")
    pdf.table_row("TOOLS_DAILY_SWEEP_REPORT_SECRET_NAME", "peq-tools-daily-sweep-report-config")
    pdf.table_row("TOOLS_SKIP_GCP", "1 = skip SM + Linear + email (tests)")
    pdf.table_row("TOOLS_DAILY_SWEEP_REPORT_DRY_RUN", "1 = build report, no send")
    pdf.h2("Secret JSON schema (values in Secret Manager only)")
    pdf.code(
        """{
  "gmail_address": "reports-bot@gmail.com",
  "gmail_app_password": "xxxx xxxx xxxx xxxx",
  "send_to": "team@platformeq.com",
  "linear_api_key": "lin_api_..."
}"""
    )
    pdf.body(
        "Terraform creates the secret container in infra/terraform/jobs.tf. Values are added "
        "with gcloud secrets versions add -- never committed to git or Terraform state."
    )
    pdf.code(
        """gcloud secrets versions add peq-tools-daily-sweep-report-config --data-file=- <<'EOF'
{"gmail_address":"...","gmail_app_password":"...","send_to":"...","linear_api_key":"..."}
EOF"""
    )

    # 11 GCP Integration
    pdf.add_page()
    pdf.h1("11", "GCP Integration (Detailed)")
    pdf.body(
        "The job runs in GCP project peq-tools (region us-central1). It uses the same "
        "platform primitives as the rest of tools-gcp: Secret Manager, Artifact Registry, "
        "Cloud Run service account identity, and Cloud Logging."
    )
    pdf.h2("GCP services involved")
    pdf.table_row("Secret Manager", "Stores Linear + Gmail credentials (JSON)")
    pdf.table_row("Artifact Registry", "Docker image: .../tools-gcp/tools-gcp:latest")
    pdf.table_row("Cloud Run (Job)", "Target host for scheduled execution (planned)")
    pdf.table_row("Cloud Scheduler", "Cron trigger Mon-Fri 9am ET (planned)")
    pdf.table_row("Cloud Logging", "Stdout/stderr from job runs")
    pdf.table_row("Cloud Monitoring", "Optional alerts on job failure")
    pdf.table_row("IAM", "Service account permissions, no key files")
    pdf.h2("Terraform resources (jobs.tf)")
    pdf.bullet("google_secret_manager_secret.daily_sweep_report_config")
    pdf.bullet("IAM: tools-gcp-run SA gets secretAccessor on job secret")
    pdf.bullet("IAM: developers get secretAccessor for local dev")
    pdf.bullet("Output: daily_sweep_report_secret")
    pdf.h2("How the job reads secrets at runtime")
    pdf.diagram(
        """  Cloud Run Job container starts
    |
    |  Attached identity: tools-gcp-run@peq-tools.iam.gserviceaccount.com
    |  (no JSON key file on disk)
    v
  tools-daily-sweep-report runs
    |
    v
  tools.secrets.get_secret("peq-tools-daily-sweep-report-config")
    |
    v
  Secret Manager API (ADC / metadata server)
    |
    v
  Returns latest secret version payload (JSON)
    |
    v
  Parsed into ReportSecrets dataclass"""
    )
    pdf.body(
        "Locally, ADC comes from gcloud auth application-default login. On Cloud Run, "
        "the metadata server provides tokens for the attached service account automatically."
    )

    # 12 Current vs target
    pdf.add_page()
    pdf.h1("12", "Hosting on GCP: Current vs Target")
    pdf.h2("Current state (implemented today)")
    pdf.bullet("Job code complete under src/jobs/daily-sweep-report/")
    pdf.bullet("CLI: tools-daily-sweep-report (also make daily-sweep-report for dry-run)")
    pdf.bullet("Secret container defined in Terraform (jobs.tf)")
    pdf.bullet("Unit tests in tests/jobs/daily_sweep_report/")
    pdf.bullet("Same Docker image as the FastAPI service (tools-gcp)")
    pdf.bullet("Manual or local execution; Cloud Scheduler not yet in Terraform")
    pdf.h2("Target state (recommended production hosting)")
    pdf.body(
        "Batch jobs like this should run as a Cloud Run Job, not the long-lived Cloud Run "
        "Service (which runs tools-serve / FastAPI). Cloud Run Jobs start, run the command, "
        "and exit -- ideal for cron workloads."
    )
    pdf.table_row("Cloud Run Service", "tools-serve -- /health, /ready (always on)")
    pdf.table_row("Cloud Run Job", "tools-daily-sweep-report -- runs and exits")
    pdf.table_row("Image", "Same image; different command override")
    pdf.note(
        "Cloud Run Job + Scheduler Terraform is the next infrastructure step. "
        "The job code is ready for it today."
    )

    # 13 Architecture
    pdf.add_page()
    pdf.h1("13", "Cloud Run Job + Scheduler Architecture")
    pdf.diagram(
        """  Cloud Scheduler (cron: Mon-Fri 14:00 UTC ~= 9am EST)
    |
    |  HTTP POST + OIDC token
    v
  Cloud Run Jobs API
    |
    v
  Cloud Run Job: daily-sweep-report
    |  image: us-central1-docker.pkg.dev/peq-tools/tools-gcp/tools-gcp:latest
    |  command: ["tools-daily-sweep-report"]
    |  serviceAccount: tools-gcp-run@peq-tools.iam.gserviceaccount.com
    |  env: TOOLS_GCP_PROJECT=peq-tools
    |       TOOLS_DAILY_SWEEP_REPORT_SECRET_NAME=peq-tools-daily-sweep-report-config
    v
  Container execution (~30-60 seconds)
    |-- Secret Manager (read credentials)
    |-- Linear API (fetch issues)
    |-- Gmail SMTP (send email)
    v
  Exit 0 (success) or non-zero (failure logged)"""
    )
    pdf.h2("Suggested schedule")
    pdf.code(
        """# Cloud Scheduler (America/New_York aware)
# Option A: 0 14 * * 1-5  (14:00 UTC -- 9am EST standard time; 10am EDT)
# Option B: timezone=America/New_York cron=0 9 * * 1-5  (always 9am local)"""
    )
    pdf.body(
        "Option B is preferred so the report always runs at 9:00 AM Eastern regardless of "
        "DST. The original GitHub workflow used 0 14 * * 1-5 UTC."
    )
    pdf.h2("Deployment pipeline")
    pdf.body(
        "GitHub Actions (WIF) builds and pushes the Docker image on merge to main. "
        "The Cloud Run Job references :latest or a pinned digest. Updating the job does "
        "not require redeploying Scheduler -- only the Job template image/command."
    )

    # 14 IAM
    pdf.add_page()
    pdf.h1("14", "IAM, Identity & Security Model")
    pdf.h2("Principles (from docs/SECRETS.md)")
    pdf.bullet("No service account JSON keys on disk or in git")
    pdf.bullet("Secret values only in Secret Manager")
    pdf.bullet("Secret names in code and Terraform are fine")
    pdf.bullet("Audit logging on Secret Manager DATA_READ enabled")
    pdf.h2("Identity matrix")
    pdf.table_row("Local dev", "Your user ADC via gcloud auth application-default login")
    pdf.table_row("Cloud Run Job", "tools-gcp-run@peq-tools.iam.gserviceaccount.com")
    pdf.table_row("Scheduler invoker", "Dedicated SA with run.invoker on the Job (planned)")
    pdf.table_row("CI (GitHub Actions)", "TOOLS_SKIP_GCP=1 -- no GCP in unit tests")
    pdf.h2("Minimum IAM for the runtime SA")
    pdf.bullet("roles/secretmanager.secretAccessor on peq-tools-daily-sweep-report-config")
    pdf.bullet("roles/logging.logWriter (project) -- Cloud Run logs")
    pdf.body(
        "The job does not need GCS, BigQuery, or Artifact Registry at runtime -- only Secret "
        "Manager read and outbound HTTPS (Linear + Gmail)."
    )

    # 15 Local dev
    pdf.h1("15", "Local Development & Testing")
    pdf.code(
        """# Install
make install

# Dry run (no GCP, no email)
make daily-sweep-report
# or: TOOLS_SKIP_GCP=1 tools-daily-sweep-report --dry-run

# Live run against real Linear + Gmail
gcloud auth application-default login
gcloud config set project peq-tools
tools-daily-sweep-report

# Tests
make test   # includes 8 daily-sweep-report tests"""
    )
    pdf.h2("Test coverage")
    pdf.bullet("Monday -> Friday date logic")
    pdf.bullet("Tuesday -> Monday date logic")
    pdf.bullet("Issue matching by title + assignee")
    pdf.bullet("Email subject and HTML content")
    pdf.bullet("Secret schema validation")
    pdf.bullet("run() with TOOLS_SKIP_GCP=1")

    # 16 Migration
    pdf.add_page()
    pdf.h1("16", "Migration from GitHub Actions")
    pdf.h2("Before (GitHub Actions)")
    pdf.bullet("Cron in .github/workflows with inline Python heredoc")
    pdf.bullet("Secrets: GMAIL_ADDRESS, APP_PASSWORD, SEND_TO, LINEAR_API_KEY")
    pdf.bullet("Ran on ubuntu-latest GitHub runner")
    pdf.h2("After (tools-gcp on GCP)")
    pdf.bullet("Modular Python package under src/jobs/daily-sweep-report/")
    pdf.bullet("Secrets in peq-tools-daily-sweep-report-config (JSON)")
    pdf.bullet("Runs on Cloud Run Job in peq-tools (planned schedule)")
    pdf.bullet("CI runs unit tests only; no secrets in GitHub")
    pdf.body(
        "GitHub Actions can remain for deploy (WIF -> Artifact Registry -> Cloud Run). "
        "The report cron moves off GitHub entirely."
    )

    # 17 Ops
    pdf.h1("17", "Operations, Monitoring & Troubleshooting")
    pdf.h2("Where to look when something fails")
    pdf.table_row("Job logs", "Cloud Logging -> Cloud Run Job execution logs")
    pdf.table_row("Secret access", "Cloud Audit Logs -> Secret Manager DATA_READ")
    pdf.table_row("Scheduler", "Cloud Scheduler execution history")
    pdf.h2("Common failures")
    pdf.table_row("403 Secret Manager", "SA missing secretAccessor on job secret")
    pdf.table_row("Linear 401/403", "Invalid or expired linear_api_key in secret")
    pdf.table_row("Gmail auth error", "Wrong app password or 2FA not enabled")
    pdf.table_row("Empty report / all Missing", "Wrong date window or titles don't match")
    pdf.table_row("ModuleNotFoundError", "pip install -e . after adding job package")
    pdf.h2("Manual re-run")
    pdf.body(
        "Execute the Cloud Run Job manually from Console or: "
        "gcloud run jobs execute daily-sweep-report --region us-central1"
    )

    # 18 Future jobs
    pdf.h1("18", "Future Jobs in tools-gcp")
    pdf.body(
        "daily-sweep-report establishes the pattern for all future utilities:"
    )
    pdf.bullet("src/jobs/<kebab-name>/ -- isolated code")
    pdf.bullet("tools-<kebab-name> CLI entry point")
    pdf.bullet("Optional Secret Manager container in infra/terraform/jobs.tf")
    pdf.bullet("Optional Cloud Run Job + Scheduler in Terraform")
    pdf.bullet("Tests under tests/jobs/<snake_name>/")
    pdf.body(
        "The FastAPI service (tools-serve) remains the platform health shell. Jobs share "
        "the Docker image but use different commands. This keeps one repo, one deploy "
        "pipeline, and many isolated batch utilities."
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build_pdf()
