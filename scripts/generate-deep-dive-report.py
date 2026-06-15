#!/usr/bin/env python3
"""Generate a deep-dive technical report PDF for tools-gcp."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "tools-gcp-deep-dive-report.pdf"

BLUE_DARK = (15, 52, 96)
BLUE_MID = (30, 90, 160)
BLUE_LIGHT = (60, 130, 200)
GREY_DARK = (40, 40, 40)
GREY_MID = (80, 80, 80)
GREY_LIGHT = (150, 150, 150)
WHITE = (255, 255, 255)
BG_CODE = (245, 247, 250)
BG_NOTE = (255, 253, 235)
BG_WARN = (255, 243, 243)
BG_TIP = (240, 255, 245)
ACCENT_ORANGE = (220, 100, 30)
ACCENT_GREEN = (30, 140, 80)
ACCENT_RED = (180, 40, 40)


class DeepDivePDF(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self._current_section = ""

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_fill_color(*BLUE_DARK)
        self.rect(0, 0, 210, 12, "F")
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*WHITE)
        self.set_xy(10, 2)
        self.cell(130, 8, "tools-gcp  --  Deep Dive Technical Report")
        self.set_xy(140, 2)
        self.cell(60, 8, self._current_section, align="R")
        self.ln(14)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_fill_color(*BLUE_DARK)
        self.rect(0, 283, 210, 14, "F")
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*WHITE)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def cover_page(self) -> None:
        self.set_fill_color(*BLUE_DARK)
        self.rect(0, 0, 210, 297, "F")

        self.set_y(55)
        self.set_font("Helvetica", "B", 36)
        self.set_text_color(*WHITE)
        self.multi_cell(0, 14, "tools-gcp", align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 16)
        self.set_text_color(180, 210, 255)
        self.multi_cell(0, 9, "Deep Dive Technical Report", align="C", new_x="LMARGIN", new_y="NEXT")

        self.ln(6)
        self.set_fill_color(*BLUE_LIGHT)
        self.rect(30, self.get_y(), 150, 1, "F")
        self.ln(8)

        self.set_font("Helvetica", "", 12)
        self.set_text_color(210, 230, 255)
        self.multi_cell(
            0, 7,
            "A comprehensive walkthrough of the GCP non-prod\n"
            "platform boilerplate: architecture, code, infrastructure,\n"
            "CI/CD, and improvement recommendations.",
            align="C",
            new_x="LMARGIN", new_y="NEXT",
        )

        self.ln(20)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*WHITE)

        labels = [
            ("Audience", "Technical team members and contributors"),
            ("Phase", "Phase 1 -- Clone-to-Running Foundation"),
            ("Scope", "src/, infra/terraform/, docs/, .github/, scripts/"),
            ("Date", "June 2026"),
        ]
        for label, val in labels:
            self.set_x(45)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(160, 200, 255)
            self.cell(35, 7, label + ":")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*WHITE)
            self.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")

        self.ln(30)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(120, 160, 210)
        self.multi_cell(
            0, 6,
            "Generated from the live repository. Consult docs/CLONE_TO_RUNNING.md for the\n"
            "authoritative acceptance checklist.",
            align="C",
        )

    def toc_entry(self, num: str, title: str, page: str = "") -> None:
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*GREY_DARK)
        self.set_x(15)
        self.cell(12, 7, num)
        self.cell(150, 7, title)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(*GREY_LIGHT)
        self.cell(0, 7, page, align="R", new_x="LMARGIN", new_y="NEXT")

    def toc_sub(self, title: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY_MID)
        self.set_x(27)
        self.cell(10, 6, "--")
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")

    def h1(self, num: str, title: str) -> None:
        self._current_section = f"{num}  {title}"
        self.ln(4)
        self.set_fill_color(*BLUE_DARK)
        self.rect(10, self.get_y(), 190, 11, "F")
        self.set_y(self.get_y() + 1)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*WHITE)
        self.set_x(14)
        self.cell(0, 9, f"{num}  {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*GREY_DARK)
        self.ln(4)

    def h2(self, title: str) -> None:
        self.ln(3)
        self.set_fill_color(*BLUE_MID)
        self.rect(10, self.get_y(), 4, 7, "F")
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*BLUE_DARK)
        self.set_x(16)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*GREY_DARK)
        self.ln(2)

    def h3(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*BLUE_MID)
        self.multi_cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*GREY_DARK)
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def bullet(self, text: str, indent: int = 0) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY_DARK)
        x = self.get_x() + 5 + indent
        self.set_x(x)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*BLUE_MID)
        self.cell(6, 5.5, "\x95")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")

    def code_block(self, code: str, label: str = "") -> None:
        self.ln(1)
        if label:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GREY_LIGHT)
            self.set_x(12)
            self.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_fill_color(*BG_CODE)
        self.set_draw_color(*BLUE_LIGHT)
        y_start = self.get_y()
        self.rect(10, y_start, 190, 4, "F")
        lines = code.strip().split("\n")
        line_h = 5.2
        total_h = len(lines) * line_h + 6
        self.set_fill_color(*BG_CODE)
        self.rect(10, y_start, 190, total_h, "FD")
        self.set_y(y_start + 2)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(20, 40, 80)
        for line in lines:
            self.set_x(14)
            self.cell(0, line_h, line, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def callout(self, text: str, kind: str = "note") -> None:
        colors = {
            "note": (BG_NOTE, ACCENT_ORANGE, "NOTE"),
            "tip": (BG_TIP, ACCENT_GREEN, "TIP"),
            "warn": (BG_WARN, ACCENT_RED, "WARNING"),
        }
        bg, border, label = colors.get(kind, colors["note"])
        self.ln(2)
        y = self.get_y()
        self.set_fill_color(*bg)
        self.set_draw_color(*border)
        self.rect(10, y, 3, 100, "F")
        self.set_xy(14, y)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*border)
        self.cell(0, 5.5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_x(14)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY_DARK)
        self.multi_cell(186, 5.5, text, new_x="LMARGIN", new_y="NEXT")
        end_y = self.get_y()
        self.set_fill_color(*bg)
        self.rect(10, y, 3, end_y - y + 2, "F")
        self.ln(3)

    def table_header(self, cols: list[tuple[str, float]]) -> None:
        self.set_fill_color(*BLUE_DARK)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        for label, width in cols:
            self.cell(width, 7, label, fill=True, border=0)
        self.ln()
        self._table_cols = cols
        self._table_row_idx = 0

    def table_row(self, values: list[str]) -> None:
        bg = (248, 250, 254) if self._table_row_idx % 2 == 0 else WHITE
        self.set_fill_color(*bg)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY_DARK)
        x_start = self.get_x()
        y_start = self.get_y()
        max_h = 5.5
        for (_, width), val in zip(self._table_cols, values):
            self.set_xy(x_start, y_start)
            lines = self.multi_cell(width, 5.5, val, fill=True, border=0, dry_run=True, output="LINES")
            h = max(5.5, len(lines) * 5.5)
            if h > max_h:
                max_h = h
            x_start += width
        x_start = self.get_x()
        for (_, width), val in zip(self._table_cols, values):
            self.set_xy(x_start, y_start)
            self.multi_cell(width, 5.5, val, fill=True, border=0, new_x="RIGHT", new_y="TOP")
            x_start += width
        self.set_y(y_start + max_h)
        self.ln(0)
        self._table_row_idx += 1

    def divider(self) -> None:
        self.ln(2)
        self.set_draw_color(*BLUE_LIGHT)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)


def build_pdf() -> None:
    pdf = DeepDivePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.set_margins(10, 18, 10)

    # -- COVER PAGE ----------------------------------------------------------
    pdf.add_page()
    pdf.cover_page()

    # -- TABLE OF CONTENTS ---------------------------------------------------
    pdf.add_page()
    pdf._current_section = "Table of Contents"
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*BLUE_DARK)
    pdf.ln(4)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.set_fill_color(*BLUE_MID)
    pdf.rect(10, pdf.get_y(), 190, 1, "F")
    pdf.ln(5)

    toc_items = [
        ("1", "The Big Picture -- How Everything Fits Together"),
        ("2", "Application Code Deep Dive  (src/tools/)"),
        ("3", "Infrastructure Deep Dive  (infra/terraform/)"),
        ("4", "Documentation Deep Dive  (docs/)"),
        ("5", "GitHub Actions CI Deep Dive  (.github/workflows/)"),
        ("6", "Scripts Deep Dive  (scripts/)"),
        ("7", "End-to-End Flow  -- From Clone to Live Service"),
        ("8", "Common Errors & Troubleshooting"),
        ("9", "Improvement Recommendations"),
        ("10", "Quick Reference Cheat Sheet"),
    ]
    subs = {
        "1": ["Authentication model", "Zero-secrets invariant", "How the components connect"],
        "2": ["config.py", "secrets.py", "app.py", "tests/test_app.py", "pyproject.toml & Dockerfile"],
        "3": ["versions.tf", "variables.tf", "apis.tf", "iam.tf", "resources.tf", "outputs.tf"],
        "4": ["SECRETS.md", "GIT_STANDARDS.md", "GCP_SETUP.md", "CLONE_TO_RUNNING.md"],
        "5": ["ci.yml -- step by step", "PR template walkthrough"],
        "6": ["bootstrap-project.sh", "verify-setup.sh"],
        "7": ["Day-zero admin setup", "Developer clone-to-running", "Deploy to Cloud Run"],
        "8": ["Auth & credential errors", "Terraform errors", "Deploy errors"],
        "9": ["Eight actionable improvements"],
        "10": ["Make targets", "Env vars", "IAM roles", "Key commands"],
    }
    for num, title in toc_items:
        pdf.toc_entry(num, title)
        for sub in subs.get(num, []):
            pdf.toc_sub(sub)
        pdf.ln(1)

    # ========================================================================
    # SECTION 1 -- THE BIG PICTURE
    # ========================================================================
    pdf.add_page()
    pdf.h1("1", "The Big Picture -- How Everything Fits Together")

    pdf.body(
        "tools-gcp is a non-production GCP development platform for the Peq team. Its purpose "
        "is narrowly defined: prove that a developer can clone this repository, authenticate with "
        "Google Cloud (using gcloud -- no credential files on disk), run the application locally, "
        "and deploy it to Cloud Run -- all without ever storing secrets in git or on disk."
    )
    pdf.body(
        "Think of it as the \"empty but wired\" house before you move in the furniture. The healthcare "
        "data pipeline (Dataproc, Composer, medallion layers) is the furniture -- it will run on this "
        "platform later. Phase 1 is purely about proving the wiring."
    )

    pdf.h2("1.1  Authentication Model")
    pdf.body(
        "The single most important design decision in this repo is HOW secrets are handled. "
        "There are three runtime contexts, and each uses a different auth mechanism:"
    )
    pdf.code_block("""\
  Context             Auth Mechanism                        Notes
  ------------------- ------------------------------------- --------------------------
  Local development   gcloud auth application-default login Credentials stored in OS
                      (ADC -- Application Default Creds)     keychain, NOT in the repo
  Cloud Run (deployed) Attached service account identity    No key file ever created
                      (tools-gcp-run@...)               or downloaded
  GitHub Actions CI   TOOLS_SKIP_GCP=1                 GCP calls are skipped;
                      (no GCP creds at all in Phase 1)      lint + unit tests only""",
    label="Authentication contexts")

    pdf.callout(
        "Application Default Credentials (ADC) is a GCP standard: the Google Cloud SDK checks "
        "for credentials in a specific order (env var -> well-known file -> metadata server). When "
        "you run 'gcloud auth application-default login', it writes to ~/.config/gcloud/ on your "
        "machine -- completely outside the repo directory. The Python SDK picks this up automatically "
        "with no extra code.",
        kind="note",
    )

    pdf.h2("1.2  The Zero-Secrets Invariant")
    pdf.body(
        "Every design decision in this repo flows from one rule: secret VALUES never touch disk "
        "inside the repo. Secret NAMES (like 'peq-tools-app-config') are fine in code "
        "and config -- they are not sensitive. The distinction is critical."
    )
    pdf.table_header([("Item", 55), ("Allowed in repo?", 40), ("Why", 95)])
    pdf.table_row(["Secret name (e.g. 'app-config')", "YES", "Not sensitive -- it is just an identifier"])
    pdf.table_row(["Secret value (password, token, key)", "NEVER", "Would be in git history forever"])
    pdf.table_row([".env with placeholder values only", "YES (.env.example)", "Documents var names, no real values"])
    pdf.table_row([".env with real values", "NEVER", ".gitignore blocks it but policy also forbids"])
    pdf.table_row(["Service account JSON key", "NEVER", "Key persists; Cloud Run SA is used instead"])
    pdf.table_row(["Environment variable: project ID", "YES", "Not a secret -- it's just a string label"])
    pdf.table_row(["Environment variable: secret value", "NEVER", "Plaintext in Cloud Run revision history"])
    pdf.ln(3)

    pdf.h2("1.3  How the Components Connect")
    pdf.body(
        "Here is the relationship between every major part of the repository:"
    )
    pdf.code_block("""\
  +-----------------------------------------------------------------+
  |                    DEVELOPER MACHINE                            |
  |                                                                 |
  |  git clone -> make install -> cp .env.example .env -> make dev    |
  |                                                                 |
  |  gcloud auth ADC  ------------------------------------------+  |
  |  (OS keychain)                                               |  |
  +------------------------------------------------------------ | -+
                                                                |
                      +-----------------------------------------+
                      |  ADC credentials (never leaves keychain)
                      v
  +---------------------------------------------------------------+
  |                   GCP PROJECT (peq-tools)            |
  |                                                               |
  |  Secret Manager <- app reads 'peq-tools-app-config'  |
  |  Cloud Run      <- make deploy pushes Docker image here       |
  |  Artifact Reg.  <- Docker image is stored here first          |
  |  Cloud Build    <- builds the Docker image from source        |
  |  GCS Bucket     <- dev sandbox (future data pipeline)         |
  |  BigQuery       <- future analytics workloads                 |
  +---------------------------------------------------------------+
                      ^
                      |  Terraform provisions all of the above
  +-------------------+-------------------------------------------+
  |              infra/terraform/  (run once by admin)            |
  |  apis.tf -> enable APIs    iam.tf -> grant developer roles      |
  |  resources.tf -> bucket, secret, SA, Artifact Registry        |
  +---------------------------------------------------------------+

  GitHub Actions (.github/workflows/ci.yml)
  +-- on every push/PR to main: ruff lint + pytest (no GCP creds)""",
    label="Component relationship diagram")

    # ========================================================================
    # SECTION 2 -- APPLICATION CODE
    # ========================================================================
    pdf.add_page()
    pdf.h1("2", "Application Code Deep Dive  (src/tools/)")

    pdf.body(
        "The application lives in src/tools/ and follows the 'src layout' convention for Python "
        "packages. This means the source code is under src/ rather than at the root, which prevents "
        "import confusion and forces proper installation. There are four files:"
    )
    pdf.code_block("""\
  src/
  +-- tools/
      +-- __init__.py    Package marker + version string
      +-- config.py      Reads environment variables into a typed Settings object
      +-- secrets.py     Talks to GCP Secret Manager via Application Default Credentials
      +-- app.py         FastAPI application with /health and /ready endpoints""",
    label="src/ layout")

    pdf.h2("2.1  config.py -- Environment Variables -> Typed Settings")
    pdf.body(
        "This module solves a small but important problem: environment variables are always strings, "
        "and you don't want scattered os.environ.get() calls across every file. config.py reads all "
        "non-secret configuration once and returns a frozen (immutable) dataclass."
    )
    pdf.code_block("""\
  @dataclass(frozen=True)          # 'frozen' means it's immutable after creation
  class Settings:
      gcp_project: str             # e.g. "peq-tools"
      gcp_region:  str             # e.g. "us-central1"
      secret_name: str             # e.g. "peq-tools-app-config"
      environment: str             # e.g. "nonprod"
      skip_gcp:    bool            # True when TOOLS_SKIP_GCP=1

  @classmethod
  def from_env(cls) -> Settings:   # reads from os.environ with fallback defaults
      ...""", label="config.py -- key structure")

    pdf.callout(
        "Notice that skip_gcp is the ONLY boolean here. When True, all GCP API calls are bypassed. "
        "This is set to 1 in CI (no cloud credentials) and during offline development. This pattern "
        "is intentional: one flag gates all cloud calls rather than scattered try/except blocks.",
        kind="tip",
    )
    pdf.body(
        "The five environment variables this module reads (all set in .env.example with defaults):"
    )
    pdf.table_header([("Variable", 75), ("Default", 60), ("Purpose", 55)])
    pdf.table_row(["TOOLS_GCP_PROJECT", "peq-tools", "Which GCP project to use"])
    pdf.table_row(["TOOLS_GCP_REGION", "us-central1", "Which GCP region"])
    pdf.table_row(["TOOLS_SECRET_NAME", "peq-tools-app-config", "Secret to read for /ready"])
    pdf.table_row(["TOOLS_ENVIRONMENT", "nonprod", "Label shown in /health response"])
    pdf.table_row(["TOOLS_SKIP_GCP", "(unset)", "Set to 1 to skip all GCP API calls"])
    pdf.ln(3)

    pdf.h2("2.2  secrets.py -- Secret Manager Client")
    pdf.body(
        "This module wraps the Google Cloud Secret Manager SDK. It has two public functions:"
    )
    pdf.code_block("""\
  get_secret(secret_name, *, settings) -> str
      # Fetches the LATEST version of a secret from Secret Manager.
      # Builds the full resource path:
      #   projects/peq-tools/secrets/peq-tools-app-config/versions/latest
      # Returns the secret VALUE as a decoded string.

  secret_is_accessible(*, settings) -> bool
      # Calls get_secret() and catches specific GCP exceptions:
      #   PermissionDenied  -> your account lacks secretAccessor role
      #   NotFound          -> secret doesn't exist yet (bootstrap not run)
      #   Any other error   -> unexpected failure
      # Used by the /ready endpoint to tell you if auth is working.""",
    label="secrets.py -- public API")

    pdf.body(
        "The key thing to understand: the Google Cloud SDK automatically picks up your Application "
        "Default Credentials. You never pass credentials explicitly. When "
        "secretmanager.SecretManagerServiceClient() is created, the SDK looks for auth in this order: "
        "(1) GOOGLE_APPLICATION_CREDENTIALS env var, (2) ~/.config/gcloud/application_default_credentials.json, "
        "(3) GCP metadata server (when running on Cloud Run/GCE). For local dev, step (2) is used after "
        "running 'gcloud auth application-default login'."
    )

    pdf.callout(
        "Why catch PermissionDenied and NotFound separately? Because they require different fixes. "
        "PermissionDenied means IAM is wrong (check your roles). NotFound means Terraform bootstrap "
        "hasn't been run yet. The /ready endpoint returns different messages for each, which makes "
        "debugging much faster.",
        kind="note",
    )

    pdf.h2("2.3  app.py -- The FastAPI Application")
    pdf.body(
        "The application has exactly two HTTP endpoints. That's intentional -- Phase 1 is about "
        "proving infrastructure works, not building product features."
    )
    pdf.code_block("""\
  GET /health
      Returns: {"status": "ok", "project": "peq-tools", "environment": "nonprod"}
      GCP calls: NONE. This endpoint always succeeds regardless of cloud auth.
      Used for: Cloud Run liveness probe, quick sanity check.

  GET /ready
      Returns: {"status": "ready"|"not_ready", "secret_configured": true|false}
      GCP calls: Secret Manager read (unless TOOLS_SKIP_GCP=1)
      Used for: Cloud Run readiness probe, acceptance test, auth verification.

  def main() -> None:
      # Entry point registered in pyproject.toml as 'tools-serve'
      # Reads PORT env var (Cloud Run sets this to 8080 by default)
      uvicorn.run("tools.app:app", host="0.0.0.0", port=port, reload=False)""",
    label="app.py -- endpoints")

    pdf.callout(
        "Why two separate endpoints? Cloud Run (and Kubernetes) distinguishes between liveness "
        "(is the process running?) and readiness (is it ready to serve traffic?). /health answers "
        "liveness -- it never calls GCP, so it responds even if credentials are broken. "
        "/ready answers readiness -- it only returns 'ready' once Secret Manager is accessible.",
        kind="note",
    )

    pdf.h2("2.4  tests/test_app.py")
    pdf.body(
        "The test file has two tests. Both run with TOOLS_SKIP_GCP=1 set as an environment "
        "variable so the tests never make real GCP API calls. This is how CI can run without "
        "cloud credentials."
    )
    pdf.code_block("""\
  # The file sets env vars BEFORE importing the app:
  os.environ.setdefault("TOOLS_SKIP_GCP", "1")
  os.environ.setdefault("TOOLS_GCP_PROJECT", "test-project")

  # test_health: verifies /health returns 200 with expected JSON keys
  # test_ready_skips_gcp: verifies /ready returns 'ready' when SKIP_GCP=1
  #   (because secret_is_accessible() returns True early when skip_gcp is set)""",
    label="tests/test_app.py")

    pdf.callout(
        "The fact that os.environ is set BEFORE 'from tools.app import app' is crucial. "
        "Python modules are cached after first import, so if the app were imported first, the "
        "Settings object would already be frozen with the wrong values. Order matters.",
        kind="warn",
    )

    pdf.h2("2.5  pyproject.toml, requirements.txt, and Dockerfile")
    pdf.body(
        "pyproject.toml is the single source of truth for Python packaging. It defines:"
    )
    pdf.bullet("Runtime dependencies: google-cloud-secret-manager, google-auth, fastapi, uvicorn")
    pdf.bullet("Dev dependencies (optional): pytest, httpx, ruff")
    pdf.bullet("The 'tools-serve' entry point that maps to app.py's main() function")
    pdf.bullet("pytest configuration: testpaths=['tests'], pythonpath=['src']")
    pdf.bullet("ruff configuration: line-length=100, Python 3.11 target, E/F/I/W rules")
    pdf.ln(2)
    pdf.body(
        "requirements.txt is a secondary, simplified file kept for Docker builds and pip-only "
        "installs (CI contexts that don't want the full pyproject.toml machinery). It mirrors "
        "the runtime deps from pyproject.toml. Both must be kept in sync when adding dependencies."
    )
    pdf.body(
        "The Dockerfile uses Python 3.11-slim (minimal base, no extras). Key points:"
    )
    pdf.code_block("""\
  FROM python:3.11-slim

  ENV PYTHONDONTWRITEBYTECODE=1   # no .pyc files (smaller image)
      PYTHONUNBUFFERED=1          # stdout/stderr not buffered (log immediately)
      PORT=8080

  COPY pyproject.toml requirements.txt ./
  COPY src/ ./src/

  RUN pip install --no-cache-dir .   # installs the package (reads pyproject.toml)

  CMD ["tools-serve"]           # runs the entry point""",
    label="Dockerfile -- annotated")

    pdf.callout(
        "No secrets are EVER baked into the Docker image. The image contains only code and "
        "configuration names. When Cloud Run starts the container, it injects env vars for "
        "project ID and region via --set-env-vars in the Makefile deploy target. Secret VALUES "
        "are fetched at runtime from Secret Manager by the running container.",
        kind="tip",
    )

    # ========================================================================
    # SECTION 3 -- TERRAFORM
    # ========================================================================
    pdf.add_page()
    pdf.h1("3", "Infrastructure Deep Dive  (infra/terraform/)")

    pdf.body(
        "Terraform manages all GCP resources declaratively. 'Declaratively' means you describe "
        "what you WANT to exist, and Terraform figures out how to create/update/delete resources "
        "to match that description. If you run terraform apply twice, the second run does nothing "
        "-- it is idempotent."
    )
    pdf.body(
        "All Terraform files are in infra/terraform/. There are six .tf files plus an example "
        "variables file:"
    )
    pdf.code_block("""\
  infra/terraform/
  +-- versions.tf           Terraform version requirements + Google provider config
  +-- variables.tf          Input variable declarations (project_id, region, member, ...)
  +-- apis.tf               Enables the 7 GCP APIs this project needs
  +-- iam.tf                Grants developer and Cloud Run SA IAM roles
  +-- resources.tf          Creates GCS bucket, Secret Manager secret, SA, Artifact Registry
  +-- outputs.tf            Prints useful values after terraform apply
  +-- terraform.tfvars.example   Template -> copy to terraform.tfvars before apply""",
    label="infra/terraform/ layout")

    pdf.h2("3.1  versions.tf -- Provider Requirements")
    pdf.body(
        "This file pins the minimum Terraform version (1.5+) and the Google provider version "
        "(~> 5.0, meaning any 5.x release). The provider block tells Terraform which GCP project "
        "and region to operate in -- it reads these from input variables."
    )
    pdf.code_block("""\
  terraform {
    required_version = ">= 1.5"
    required_providers {
      google = { source = "hashicorp/google", version = "~> 5.0" }
    }
  }
  provider "google" {
    project = var.project_id    # comes from terraform.tfvars
    region  = var.region
  }""", label="versions.tf")

    pdf.callout(
        "The provider does NOT have credentials = ... . This is intentional. Terraform picks "
        "up Application Default Credentials the same way the Python SDK does -- from gcloud auth. "
        "This is why 'gcloud auth application-default login' is required before running terraform.",
        kind="note",
    )

    pdf.h2("3.2  variables.tf -- Input Variables")
    pdf.body(
        "Variables make Terraform reusable across environments. Instead of hardcoding "
        "'peq-tools' everywhere, you set it once in terraform.tfvars."
    )
    pdf.table_header([("Variable", 40), ("Type", 22), ("Default", 45), ("Purpose", 83)])
    pdf.table_row(["project_id", "string", "(required)", "GCP project ID -- no default, must be set"])
    pdf.table_row(["region", "string", "us-central1", "Primary GCP region for all resources"])
    pdf.table_row(["member", "string", "(required)", "IAM member: 'user:you@example.com'"])
    pdf.table_row(["environment", "string", "nonprod", "Label applied to GCP resource tags"])
    pdf.table_row(["app_name", "string", "tools-gcp", "Used for SA name, AR repo, Cloud Run service"])
    pdf.ln(3)

    pdf.h2("3.3  apis.tf -- Enabling GCP APIs")
    pdf.body(
        "GCP services are disabled by default on new projects. You must explicitly enable each "
        "API before you can use it. apis.tf enables seven APIs using a Terraform 'for_each' loop "
        "-- one google_project_service resource is created for each API in the list."
    )
    pdf.table_header([("API", 90), ("Why it's needed", 100)])
    pdf.table_row(["run.googleapis.com", "Deploy and run containerized services (Cloud Run)"])
    pdf.table_row(["secretmanager.googleapis.com", "Store and read secret values at runtime"])
    pdf.table_row(["storage.googleapis.com", "GCS buckets for dev sandbox and future pipeline data"])
    pdf.table_row(["bigquery.googleapis.com", "Future analytics and medallion pipeline workloads"])
    pdf.table_row(["artifactregistry.googleapis.com", "Store Docker images before deploying to Cloud Run"])
    pdf.table_row(["cloudbuild.googleapis.com", "Build Docker images from source via 'gcloud builds submit'"])
    pdf.table_row(["iam.googleapis.com", "Manage service accounts and IAM bindings via Terraform"])
    pdf.ln(3)

    pdf.callout(
        "disable_on_destroy = false is set on every API resource. This means running "
        "'terraform destroy' will NOT disable these APIs. Why? Disabling APIs can break things "
        "that are already using them, and re-enabling takes several minutes. For a non-prod "
        "project you're tearing down and rebuilding, leaving APIs enabled is safer.",
        kind="note",
    )

    pdf.h2("3.4  iam.tf -- Developer Roles and Cloud Run SA")
    pdf.body(
        "IAM controls who can do what in GCP. iam.tf grants seven roles to the developer "
        "(var.member) and one role to the Cloud Run service account. All roles are at the "
        "project level -- acceptable for non-prod, where least-privilege is enforced at "
        "the project boundary rather than per-resource."
    )
    pdf.table_header([("Role", 80), ("Required for", 110)])
    pdf.table_row(["roles/bigquery.user", "Run BigQuery jobs and queries (future pipeline)"])
    pdf.table_row(["roles/run.developer", "Deploy services to Cloud Run, view logs"])
    pdf.table_row(["roles/storage.objectAdmin", "Read/write objects in the dev sandbox GCS bucket"])
    pdf.table_row(["roles/secretmanager.secretAccessor", "Read secret values from Secret Manager at runtime"])
    pdf.table_row(["roles/artifactregistry.writer", "Push Docker images to the Artifact Registry repo"])
    pdf.table_row(["roles/cloudbuild.builds.editor", "Submit builds via 'gcloud builds submit'"])
    pdf.table_row(["roles/iam.serviceAccountUser", "Impersonate the Cloud Run SA when deploying"])
    pdf.ln(2)
    pdf.body(
        "The Cloud Run service account (google_service_account.cloud_run) is created in resources.tf "
        "and granted only ONE role: secretmanager.secretAccessor. This is the principle of least "
        "privilege applied to the runtime identity -- the deployed container can ONLY read secrets, "
        "nothing else."
    )

    pdf.h2("3.5  resources.tf -- GCP Resources")
    pdf.body("Four resources are created:")
    pdf.h3("GCS Bucket  (google_storage_bucket.dev_sandbox)")
    pdf.body(
        "Named {project_id}-dev-sandbox. A sandbox bucket for development artifacts and future "
        "pipeline data. uniform_bucket_level_access = true enforces IAM-only access control "
        "(disables legacy ACLs). force_destroy = true allows Terraform to delete the bucket "
        "even if it contains objects -- appropriate for a dev sandbox."
    )
    pdf.h3("Secret Manager Secret  (google_secret_manager_secret.app_config)")
    pdf.body(
        "Named {project_id}-app-config. Created with automatic replication (Google chooses "
        "regions for you -- simpler for non-prod). A second resource creates version 1 with "
        "a placeholder value 'dev-placeholder-rotate-me'. This placeholder gets the app to "
        "pass the /ready check without requiring you to manually set a real secret first."
    )
    pdf.callout(
        "IMPORTANT: The placeholder value 'dev-placeholder-rotate-me' is in the Terraform "
        "state file (terraform.tfstate), which IS a secret risk. For Phase 2, use a "
        "data source or manual initial value instead of hardcoding in resources.tf. "
        "For non-prod with a throwaway value, this is acceptable.",
        kind="warn",
    )
    pdf.h3("Cloud Run Service Account  (google_service_account.cloud_run)")
    pdf.body(
        "Named {app_name}-run@{project_id}.iam.gserviceaccount.com. This is the identity "
        "that the Cloud Run container runs as. It gets only secretAccessor. No key is ever "
        "created or downloaded -- Cloud Run attaches the SA identity automatically."
    )
    pdf.h3("Artifact Registry Repository  (google_artifact_registry_repository.app)")
    pdf.body(
        "A Docker-format repository named tools-gcp in us-central1. Docker images from "
        "'gcloud builds submit' are stored here before being deployed to Cloud Run."
    )

    pdf.h2("3.6  outputs.tf -- Printed Values After Apply")
    pdf.body(
        "After 'terraform apply', these values are printed to the terminal for easy reference:"
    )
    pdf.table_header([("Output", 60), ("Example value", 130)])
    pdf.table_row(["project_id", "peq-tools"])
    pdf.table_row(["region", "us-central1"])
    pdf.table_row(["dev_bucket", "peq-tools-dev-sandbox"])
    pdf.table_row(["secret_name", "peq-tools-app-config"])
    pdf.table_row(["cloud_run_service_account", "tools-gcp-run@peq-tools.iam.gserviceaccount.com"])
    pdf.table_row(["artifact_registry", "us-central1-docker.pkg.dev/peq-tools/tools-gcp"])
    pdf.ln(3)

    # ========================================================================
    # SECTION 4 -- DOCS
    # ========================================================================
    pdf.add_page()
    pdf.h1("4", "Documentation Deep Dive  (docs/)")

    pdf.body(
        "The docs/ directory contains four Markdown files. These are not optional reading -- they "
        "are the operational runbooks that make this repo auditable and usable by anyone on the team."
    )

    pdf.h2("4.1  SECRETS.md -- The Policy Document")
    pdf.body(
        "This is the foundational policy document. Every team member should read it on day one. "
        "It explains the two-command local auth setup, how the Python SDK picks up credentials "
        "transparently, what is forbidden, and what the audit trail looks like in GCP."
    )
    pdf.body("Key sections:")
    pdf.bullet("Authentication flow diagram: developer laptop -> gcloud -> GCP services")
    pdf.bullet("The two required local commands: gcloud auth login + application-default login")
    pdf.bullet("How to read a secret in Python (via the tools.secrets module)")
    pdf.bullet("How to create/update a secret value (gcloud CLI commands -- admin only)")
    pdf.bullet("The forbidden patterns table (6 specific things never to do)")
    pdf.bullet("Allowed environment variables (non-secret config only)")
    pdf.bullet("Audit trail: where secret access and IAM changes are logged in Cloud Audit Logs")

    pdf.h2("4.2  GIT_STANDARDS.md -- Branch, PR, and Commit Rules")
    pdf.body(
        "Defines the workflow conventions so PRs are consistent and auditable. Key sections:"
    )
    pdf.bullet("Branch naming: feature/<ticket>-<desc>, fix/<ticket>-<desc>, chore/<desc>")
    pdf.bullet("PR requirements: 1 approving review, CI pass, no direct pushes to main")
    pdf.bullet("Commit format: Conventional Commits (feat/fix/docs/chore/refactor/test/ci/infra)")
    pdf.bullet("Secrets-in-PR checklist: reviewers must confirm no keys or .env values in diff")
    pdf.bullet("GitHub branch protection settings (manual admin step -- documented here)")
    pdf.code_block("""\
  Example commit messages (Conventional Commits format):
    feat(run): add health check endpoint for Cloud Run
    infra(iam): grant developer secretmanager.secretAccessor on non-prod
    fix(secrets): handle NotFound exception in secret_is_accessible
    ci: pin Python version to 3.11 in GitHub Actions
    docs: document clone-to-running checklist""", label="Commit message examples")

    pdf.h2("4.3  GCP_SETUP.md -- Admin Bootstrap Runbook")
    pdf.body(
        "This is the runbook for the org admin (Joe) who creates the GCP project and runs "
        "Terraform. Developers don't need to read this in full, but should understand the "
        "target state it creates. Key sections:"
    )
    pdf.bullet("Prerequisites: billing account, project creation permissions, Terraform 1.5+")
    pdf.bullet("Step 1: Create the project (gcloud projects create + billing link)")
    pdf.bullet("Step 2: Apply Terraform (cd infra/terraform && terraform init && apply)")
    pdf.bullet("Developer IAM roles table (7 roles with descriptions)")
    pdf.bullet("Zero admin keys checklist (4 checks to confirm no SA keys exist)")
    pdf.bullet("Rollback instructions (terraform destroy vs. project deletion)")
    pdf.bullet("Explicit scope boundary: SaaS onboarding is Thia/Leo; healthcare pipeline is Phase 2")

    pdf.h2("4.4  CLONE_TO_RUNNING.md -- The Acceptance Checklist")
    pdf.body(
        "This is the definition of done for Phase 1. Any developer should be able to follow "
        "these 8 steps on a fresh machine and end up with a live Cloud Run service. "
        "The steps are:"
    )
    pdf.code_block("""\
  Step 1: git clone https://github.com/andrew-platformeq/tools-gcp.git
  Step 2: gcloud auth login + gcloud auth application-default login + gcloud config set project
  Step 3: ./scripts/verify-setup.sh  (confirms no secrets on disk, tools installed, auth works)
  Step 4: make install               (creates .venv/, installs package in editable mode)
  Step 5: cp .env.example .env && make dev  (starts server on :8080)
          -> curl http://localhost:8080/health  ->  {"status": "ok", ...}
          -> curl http://localhost:8080/ready   ->  {"status": "ready", "secret_configured": true}
  Step 6: make test && make lint     (all tests pass; no ruff errors)
  Step 7: make deploy && make smoke  (deploys to Cloud Run; hits /health on live URL)
  Step 8: confirm no credential files created (find command)""", label="CLONE_TO_RUNNING.md -- 8 steps")

    pdf.body(
        "The troubleshooting table at the bottom maps specific error messages to fixes -- "
        "403 Secret Manager -> check IAM, 'Could not automatically determine credentials' -> "
        "run ADC login, '/ready shows false' -> run Terraform bootstrap."
    )

    # ========================================================================
    # SECTION 5 -- GITHUB ACTIONS
    # ========================================================================
    pdf.add_page()
    pdf.h1("5", "GitHub Actions CI Deep Dive  (.github/workflows/)")

    pdf.h2("5.1  ci.yml -- Step by Step")
    pdf.body(
        "The workflow file is .github/workflows/ci.yml. It defines one job: 'lint-and-test'. "
        "This name is important -- it must exactly match what you configure in GitHub's branch "
        "protection settings as the required status check."
    )
    pdf.code_block("""\
  name: CI
  on:
    push:        { branches: [main] }
    pull_request: { branches: [main] }     # runs on EVERY PR targeting main
  permissions:
    contents: read                         # minimal permissions -- security best practice""",
    label="Trigger and permissions")

    pdf.body("The job runs on ubuntu-latest and has four steps:")
    pdf.code_block("""\
  Step 1: actions/checkout@v4
          Checks out the repository code.

  Step 2: actions/setup-python@v5  (python-version: "3.11", cache: pip)
          Installs Python 3.11 and caches pip downloads to speed up future runs.

  Step 3: pip install -e ".[dev]"
          Installs the package in editable mode WITH dev dependencies
          (pytest, httpx, ruff). The [dev] means it reads the
          [project.optional-dependencies] dev section from pyproject.toml.

  Step 4: ruff check src tests
          Runs the linter. Any style error fails the CI run.

  Step 5: pytest -q
          Runs unit tests with:
            TOOLS_GCP_PROJECT=ci-placeholder  (any string works)
            TOOLS_SKIP_GCP=1                  (no real GCP calls)
          The -q flag means 'quiet' -- only failures are printed.""",
    label="ci.yml -- job steps")

    pdf.callout(
        "Phase 1 CI deliberately has NO deploy step. Adding deployment to CI requires GitHub "
        "Workload Identity Federation -- a GCP/GitHub trust relationship that allows Actions to "
        "get short-lived GCP credentials without storing a service account key in GitHub Secrets. "
        "This is Phase 2. The reason to separate them: Phase 1 gives you fast feedback (lint + test) "
        "with zero credential risk.",
        kind="note",
    )

    pdf.h2("5.2  PR Template -- .github/pull_request_template.md")
    pdf.body(
        "When anyone opens a PR on this repo, GitHub automatically pre-fills the description "
        "with this template. It has three sections:"
    )
    pdf.bullet("Summary: space for 'what changed and why'")
    pdf.bullet("Test plan: checkboxes for make lint, make test, verify-setup.sh, manual steps")
    pdf.bullet(
        "Secrets check: three checkboxes ensuring no .env, credential JSON, or API keys in the PR; "
        "new secret names documented in .env.example; IAM changes follow least privilege"
    )
    pdf.bullet("Infra rollback section: for any Terraform or deploy changes")
    pdf.body(
        "The secrets check section is particularly important -- it forces reviewers to explicitly "
        "confirm no credentials snuck into the diff before merging."
    )

    # ========================================================================
    # SECTION 6 -- SCRIPTS
    # ========================================================================
    pdf.add_page()
    pdf.h1("6", "Scripts Deep Dive  (scripts/)")

    pdf.h2("6.1  bootstrap-project.sh -- One-Time Admin Setup")
    pdf.body(
        "This script is run ONCE by the org admin (Joe) when the GCP project doesn't exist yet. "
        "It automates the entire bootstrap sequence. It requires two environment variables:"
    )
    pdf.code_block("""\
  export BILLING_ACCOUNT=<your-billing-account-id>   # found in GCP Billing console
  export MEMBER="user:andrew@platformeq.com"          # developer's Google account
  ./scripts/bootstrap-project.sh""", label="How to run bootstrap-project.sh")

    pdf.body("What the script does, step by step:")
    pdf.code_block("""\
  1. gcloud projects create peq-tools --name="Peq Non-Prod"
     (silently ignores 'project already exists' errors)

  2. gcloud billing projects link peq-tools --billing-account=$BILLING_ACCOUNT
     (without billing, most GCP APIs are disabled)

  3. gcloud config set project peq-tools

  4. cd infra/terraform
     If terraform.tfvars doesn't exist: copies terraform.tfvars.example
     and replaces the placeholder email with $MEMBER using sed

  5. terraform init    (downloads Google provider plugin)
  6. terraform apply -auto-approve  (creates all resources)
     Passes -var flags for project_id, region, member
     so terraform.tfvars doesn't need to be committed

  7. Prints developer next steps (the gcloud auth commands)""",
    label="bootstrap-project.sh -- step by step")

    pdf.callout(
        "The -auto-approve flag skips the 'yes/no' prompt. This is safe in the bootstrap script "
        "because the script is only ever run once by an admin who knows what they're doing. "
        "Do NOT add -auto-approve to manual terraform apply runs -- always review the plan first.",
        kind="warn",
    )

    pdf.h2("6.2  verify-setup.sh -- Developer Preflight Checks")
    pdf.body(
        "Developers run this BEFORE attempting the full acceptance pass. It checks everything "
        "that could cause mysterious failures later and gives clear pass/fail/warning output."
    )
    pdf.code_block("""\
  ./scripts/verify-setup.sh
  # Output uses color coding:
  #   [OK]  (green)   = check passed
  #   [FAIL]  (red)     = hard failure (script exits 1)
  #   !  (yellow)  = warning (script continues)

  === Peq clone-to-running verification ===

  Secrets on disk:
  [OK]  No .env with secret-like values (or .env absent)
  [OK]  No credential JSON files in repo root
  [OK]  No .gcloud/ directory

  Tooling:
  [OK]  python3 installed (Python 3.11.9)
  [OK]  gcloud installed
  [OK]  git installed

  GCP authentication:
  [OK]  gcloud user authenticated (andrew@platformeq.com)
  [OK]  Application Default Credentials configured
  [OK]  gcloud project set to: peq-tools

  Python environment:
  !  .venv missing -- run: make install

  === Summary: 8 passed, 0 failed, 1 warning ==="""
    , label="verify-setup.sh -- sample output")

    pdf.body(
        "The secrets check is particularly important: it looks for .env files containing "
        "'password=', 'token=', 'key=', or 'secret=' patterns, and also for common credential "
        "file names (adc.json, credentials.json, *-key.json, etc.) in the repo root."
    )

    # ========================================================================
    # SECTION 7 -- END-TO-END FLOW
    # ========================================================================
    pdf.add_page()
    pdf.h1("7", "End-to-End Flow -- From Clone to Live Service")

    pdf.h2("7.1  Day Zero -- Admin Setup (Joe)")
    pdf.code_block("""\
  PRECONDITIONS:
  - Joe has GCP org admin permissions and a billing account ID

  ACTIONS:
  export BILLING_ACCOUNT=<id>
  export MEMBER="user:andrew@platformeq.com"
  ./scripts/bootstrap-project.sh

  WHAT HAPPENS:
  1. GCP project 'peq-tools' is created
  2. Billing linked -> APIs can now be enabled
  3. Terraform enables 7 APIs (takes ~2-5 min each on first enable)
  4. Terraform creates: IAM bindings (7 roles for Andrew), GCS bucket,
     Secret Manager secret with placeholder, Cloud Run SA, Artifact Registry repo
  5. Developer receives "next steps" printout from the script

  RESULT: GCP project is ready. Developer can now authenticate.""",
    label="Day-zero admin flow")

    pdf.h2("7.2  Developer Clone-to-Running")
    pdf.code_block("""\
  # One-time machine setup
  gcloud auth login                        # browser opens; sign in with Google account
  gcloud auth application-default login   # second browser auth for SDK credentials
  gcloud config set project peq-tools

  # Repo setup
  git clone https://github.com/andrew-platformeq/tools-gcp.git
  cd tools-gcp
  ./scripts/verify-setup.sh               # all checks should pass

  # Install and configure
  make install                            # creates .venv, installs package + dev deps
  cp .env.example .env                   # .env stays gitignored; contains no secrets

  # Run locally
  make dev                               # starts uvicorn on :8080
  curl http://localhost:8080/health      # -> {"status": "ok", "project": "peq-tools"}
  curl http://localhost:8080/ready       # -> {"status": "ready", "secret_configured": true}

  # CI passes? (same checks as GitHub Actions)
  make test && make lint                 # pytest + ruff; must pass with 0 errors""",
    label="Developer clone-to-running sequence")

    pdf.h2("7.3  Deploy to Cloud Run")
    pdf.code_block("""\
  make deploy
  # Internally runs:
  # 1. gcloud builds submit --tag us-central1-docker.pkg.dev/peq-tools/tools-gcp/tools-gcp:latest
  #    -> Cloud Build reads the Dockerfile, builds the image, pushes to Artifact Registry
  # 2. gcloud run deploy tools-gcp \\
  #      --image <artifact-registry-url> \\
  #      --region us-central1 \\
  #      --service-account tools-gcp-run@peq-tools.iam.gserviceaccount.com \\
  #      --set-env-vars "TOOLS_GCP_PROJECT=peq-tools,..."
  #    -> Cloud Run creates a new revision; routes traffic to it
  # 3. Prints the Cloud Run service URL

  make smoke
  # Hits /health and /ready on the live URL; pretty-prints JSON response
  # If /ready returns "not_ready": Secret Manager issue -- check IAM or bootstrap""",
    label="Deployment sequence")

    # ========================================================================
    # SECTION 8 -- TROUBLESHOOTING
    # ========================================================================
    pdf.add_page()
    pdf.h1("8", "Common Errors and Troubleshooting")

    pdf.h2("8.1  Auth and Credential Errors")
    pdf.table_header([("Error message", 90), ("Cause", 50), ("Fix", 50)])
    pdf.table_row([
        "Could not automatically determine credentials",
        "ADC not configured",
        "Run: gcloud auth application-default login",
    ])
    pdf.table_row([
        "403 PermissionDenied on Secret Manager",
        "Missing secretmanager.secretAccessor role",
        "Verify Terraform IAM was applied; check 'gcloud projects get-iam-policy'",
    ])
    pdf.table_row([
        "Project not found: peq-tools",
        "Project doesn't exist or wrong project set",
        "Ask Joe to run bootstrap-project.sh; run 'gcloud config set project ...'",
    ])
    pdf.table_row([
        "404 NotFound on Secret Manager",
        "Secret not created yet",
        "Run Terraform apply to create the placeholder secret",
    ])
    pdf.table_row([
        "/ready returns secret_configured: false",
        "One of the above errors",
        "Check application logs; run verify-setup.sh",
    ])
    pdf.ln(2)

    pdf.h2("8.2  Terraform Errors")
    pdf.table_header([("Error message", 90), ("Cause", 50), ("Fix", 50)])
    pdf.table_row([
        "Error: googleapi: 403 The caller does not have permission",
        "Terraform runner lacks org admin",
        "Ensure org admin runs bootstrap; check gcloud auth list",
    ])
    pdf.table_row([
        "Error: project 'X' does not have billing account",
        "Billing not linked",
        "bootstrap-project.sh handles this; or run gcloud billing projects link",
    ])
    pdf.table_row([
        "Error: API not enabled: run.googleapis.com",
        "APIs.tf hasn't been applied",
        "Run terraform apply; wait a few minutes for API enablement",
    ])
    pdf.table_row([
        "google_secret_manager_secret_version already exists",
        "Version 1 already created",
        "Safe to ignore or import existing resource: terraform import ...",
    ])
    pdf.ln(2)

    pdf.h2("8.3  Deploy Errors")
    pdf.table_header([("Error message", 90), ("Cause", 50), ("Fix", 50)])
    pdf.table_row([
        "PERMISSION_DENIED: cloudbuild.builds.create",
        "Missing roles/cloudbuild.builds.editor",
        "Verify iam.tf was applied with correct member",
    ])
    pdf.table_row([
        "PERMISSION_DENIED: artifactregistry.repositories.uploadArtifacts",
        "Missing roles/artifactregistry.writer",
        "Same as above",
    ])
    pdf.table_row([
        "Error: Cannot act as service account",
        "Missing roles/iam.serviceAccountUser",
        "Same as above -- all three deploy roles must be present",
    ])
    pdf.table_row([
        "make smoke returns HTTP 404 or 503",
        "Cloud Run not deployed or still starting",
        "Wait ~30s and retry; check 'gcloud run services describe ...'",
    ])
    pdf.ln(2)

    # ========================================================================
    # SECTION 9 -- IMPROVEMENT RECOMMENDATIONS
    # ========================================================================
    pdf.add_page()
    pdf.h1("9", "Improvement Recommendations")

    pdf.body(
        "The current boilerplate is a solid Phase 1 foundation. Below are eight concrete "
        "improvements to consider as the project grows. They are roughly ordered from "
        "most urgent to nice-to-have."
    )

    pdf.h2("9.1  Add Terraform Remote State (HIGH PRIORITY)")
    pdf.body(
        "Currently, Terraform state (terraform.tfstate) is a local file. This means only one "
        "person can run Terraform at a time, and the state is lost if the file is deleted. "
        "Remote state in a GCS bucket fixes both problems."
    )
    pdf.code_block("""\
  # Add to versions.tf:
  terraform {
    backend "gcs" {
      bucket = "peq-tools-tfstate"
      prefix = "terraform/state"
    }
    ...
  }

  # Create the state bucket manually first (chicken-and-egg):
  gsutil mb -p peq-tools -l us-central1 gs://peq-tools-tfstate
  gsutil versioning set on gs://peq-tools-tfstate""",
    label="Remote state backend (recommended addition to versions.tf)")

    pdf.callout(
        "State files can contain sensitive data (like the placeholder secret value in resources.tf). "
        "The GCS bucket should have uniform bucket-level access and only allow Terraform runners "
        "to read/write. This also enables state locking to prevent concurrent applies.",
        kind="warn",
    )

    pdf.h2("9.2  GitHub Workload Identity Federation for CI Deploy (HIGH PRIORITY)")
    pdf.body(
        "Phase 1 CI doesn't deploy. Phase 2 should add keyless CI deployment using GitHub's "
        "OIDC provider and GCP Workload Identity Federation. This avoids ever storing a "
        "service account key in GitHub Secrets."
    )
    pdf.code_block("""\
  # New Terraform resource needed (infra/terraform/wif.tf):
  resource "google_iam_workload_identity_pool" "github" {
    workload_identity_pool_id = "github-pool"
  }
  resource "google_iam_workload_identity_pool_provider" "github" {
    workload_identity_pool_id = google_iam_workload_identity_pool.github.workload_identity_pool_id
    workload_identity_pool_provider_id = "github-provider"
    oidc { issuer_uri = "https://token.actions.githubusercontent.com" }
    attribute_mapping = {
      "google.subject" = "assertion.sub"
      "attribute.repository" = "assertion.repository"
    }
    attribute_condition = "assertion.repository == 'andrew-platformeq/tools-gcp'"
  }

  # New GitHub Actions step (add to ci.yml after tests):
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: projects/.../providers/github-provider
      service_account: 'tools-gcp-deploy@peq-tools.iam.gserviceaccount.com'""",
    label="Workload Identity Federation skeleton")

    pdf.h2("9.3  Separate Deploy Service Account from Dev IAM")
    pdf.body(
        "Currently, iam.tf grants deployment roles (Cloud Build, Artifact Registry, Cloud Run) "
        "directly to the developer's user account (var.member). This means a single variable "
        "is used for both read-only developer access and deploy privileges. "
        "For a cleaner model, create a dedicated deploy SA and separate human dev roles from "
        "automation roles."
    )
    pdf.code_block("""\
  # Suggested split in iam.tf:
  variable "developers" {
    type    = list(string)   # ["user:andrew@...", "user:leo@..."]
  }
  variable "deploy_sa" {
    type    = string         # "serviceAccount:github-deploy@..."
  }
  # Grant read/develop roles to developers[]
  # Grant build/deploy roles to deploy_sa only""", label="Suggested IAM variable split")

    pdf.h2("9.4  Add a .terraform.lock.hcl File to Version Control")
    pdf.body(
        "Terraform generates a .terraform.lock.hcl file after 'terraform init' that pins "
        "provider versions exactly. The current .gitignore may be blocking this file. "
        "Committing the lock file ensures every developer gets the exact same provider version "
        "and protects against supply chain attacks on Terraform providers."
    )
    pdf.code_block("""\
  # Check infra/terraform/.gitignore -- ensure this is NOT in it:
  # .terraform.lock.hcl   <-- should be committed, not ignored

  # Correct .gitignore for infra/terraform/:
  .terraform/           # local plugin cache -- DO NOT commit
  terraform.tfstate     # local state -- DO NOT commit (use remote state instead)
  terraform.tfvars      # contains real values -- DO NOT commit
  *.tfstate.backup      # state backups -- DO NOT commit
  # .terraform.lock.hcl is intentionally NOT listed -- commit it""",
    label="Terraform .gitignore best practice")

    pdf.h2("9.5  Add Multi-Developer IAM Support")
    pdf.body(
        "iam.tf currently accepts a single var.member. As the team grows, you'll want "
        "to add developers via PR without duplicating the entire IAM block. "
        "Use a for_each over a list of members."
    )
    pdf.code_block("""\
  # variables.tf:
  variable "developers" {
    description = "List of developer IAM members"
    type        = list(string)
    default     = []
  }

  # iam.tf:
  locals {
    dev_roles = [
      "roles/bigquery.user",
      "roles/run.developer",
      "roles/storage.objectAdmin",
      "roles/secretmanager.secretAccessor",
      "roles/artifactregistry.writer",
      "roles/cloudbuild.builds.editor",
      "roles/iam.serviceAccountUser",
    ]
    dev_role_bindings = {
      for pair in setproduct(var.developers, local.dev_roles) :
      "${pair[0]}-${pair[1]}" => { member = pair[0], role = pair[1] }
    }
  }
  resource "google_project_iam_member" "developers" {
    for_each = local.dev_role_bindings
    project  = var.project_id
    role     = each.value.role
    member   = each.value.member
  }""", label="Multi-developer IAM using for_each")

    pdf.h2("9.6  Add a docker-compose.yml for Local Development")
    pdf.body(
        "Currently 'make dev' requires a manual 'cp .env.example .env' step and runs uvicorn "
        "directly. A docker-compose.yml would allow developers to run the exact production "
        "container image locally, catching Dockerfile issues before deploy."
    )
    pdf.code_block("""\
  # docker-compose.yml (suggested addition):
  services:
    api:
      build: .
      ports: ["8080:8080"]
      environment:
        TOOLS_GCP_PROJECT: peq-tools
        TOOLS_GCP_REGION: us-central1
        TOOLS_SECRET_NAME: peq-tools-app-config
        TOOLS_ENVIRONMENT: nonprod
        TOOLS_SKIP_GCP: "1"   # for offline local testing
      volumes:
        - ~/.config/gcloud:/root/.config/gcloud:ro  # mount ADC for real GCP testing""",
    label="docker-compose.yml (suggested new file)")

    pdf.h2("9.7  Add Pre-commit Hooks for Secret Scanning")
    pdf.body(
        "The current setup relies on .gitignore and human review to catch secrets. "
        "pre-commit hooks run automatically before every git commit, catching issues "
        "before they reach the remote. Recommend adding detect-secrets or gitleaks."
    )
    pdf.code_block("""\
  # .pre-commit-config.yaml (suggested new file):
  repos:
    - repo: https://github.com/Yelp/detect-secrets
      rev: v1.5.0
      hooks:
        - id: detect-secrets
          args: ['--baseline', '.secrets.baseline']
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.8.0
      hooks:
        - id: ruff

  # Install hooks:
  # pip install pre-commit
  # pre-commit install""", label=".pre-commit-config.yaml (suggested)")

    pdf.h2("9.8  Add Terraform Output to .env.example Sync")
    pdf.body(
        "Currently, developers must manually check Terraform outputs to know the correct "
        "values for TOOLS_SECRET_NAME. A small script that reads terraform output "
        "and generates a correct .env would eliminate manual copy-paste errors."
    )
    pdf.code_block("""\
  # scripts/gen-env.sh (suggested new script):
  #!/usr/bin/env bash
  cd infra/terraform
  SECRET=$(terraform output -raw secret_name 2>/dev/null)
  PROJECT=$(terraform output -raw project_id 2>/dev/null)
  REGION=$(terraform output -raw region 2>/dev/null)

  cat > ../../.env <<EOF
  TOOLS_GCP_PROJECT=${PROJECT}
  TOOLS_GCP_REGION=${REGION}
  TOOLS_SECRET_NAME=${SECRET}
  TOOLS_ENVIRONMENT=nonprod
  EOF
  echo ".env generated from Terraform outputs"
  # Add to Makefile: gen-env: infra/terraform/terraform.tfstate""",
    label="scripts/gen-env.sh (suggested new script)")

    # ========================================================================
    # SECTION 10 -- QUICK REFERENCE
    # ========================================================================
    pdf.add_page()
    pdf.h1("10", "Quick Reference Cheat Sheet")

    pdf.h2("10.1  Make Targets")
    pdf.table_header([("Target", 40), ("What it does", 150)])
    pdf.table_row(["make install", "Creates .venv/ and installs package + dev deps via pip install -e '.[dev]'"])
    pdf.table_row(["make dev", "Loads .env, runs 'tools-serve' (uvicorn on :8080 with reload=False)"])
    pdf.table_row(["make test", "Runs pytest -q with TOOLS_SKIP_GCP=1 (no GCP creds needed)"])
    pdf.table_row(["make lint", "Runs 'ruff check src tests' -- exits non-zero on any style error"])
    pdf.table_row(["make verify", "Runs scripts/verify-setup.sh -- preflight checks before acceptance pass"])
    pdf.table_row(["make deploy", "Cloud Build image + gcloud run deploy to Cloud Run (requires auth + IAM)"])
    pdf.table_row(["make smoke", "Hits /health and /ready on the deployed Cloud Run URL"])
    pdf.table_row(["make clean", "Removes .venv/, .pytest_cache/, .ruff_cache/, __pycache__ dirs"])
    pdf.ln(3)

    pdf.h2("10.2  Environment Variables")
    pdf.table_header([("Variable", 65), ("Default", 55), ("Secret?", 22), ("Set where", 48)])
    pdf.table_row(["TOOLS_GCP_PROJECT", "peq-tools", "No", ".env / Cloud Run"])
    pdf.table_row(["TOOLS_GCP_REGION", "us-central1", "No", ".env / Cloud Run"])
    pdf.table_row(["TOOLS_SECRET_NAME", "peq-tools-app-config", "No", ".env / Cloud Run"])
    pdf.table_row(["TOOLS_ENVIRONMENT", "nonprod", "No", ".env / Cloud Run"])
    pdf.table_row(["TOOLS_SKIP_GCP", "(unset)", "No", "CI / offline dev only"])
    pdf.table_row(["PORT", "8080", "No", "Cloud Run auto-sets this"])
    pdf.ln(3)

    pdf.h2("10.3  IAM Roles Reference")
    pdf.table_header([("Role", 85), ("Used by", 50), ("Allows", 55)])
    pdf.table_row(["roles/bigquery.user", "Developer", "Run queries and jobs"])
    pdf.table_row(["roles/run.developer", "Developer", "Deploy and manage Cloud Run services"])
    pdf.table_row(["roles/storage.objectAdmin", "Developer", "Read/write GCS objects"])
    pdf.table_row(["roles/secretmanager.secretAccessor", "Developer + Cloud Run SA", "Read secret values"])
    pdf.table_row(["roles/artifactregistry.writer", "Developer", "Push Docker images"])
    pdf.table_row(["roles/cloudbuild.builds.editor", "Developer", "Submit Cloud Builds"])
    pdf.table_row(["roles/iam.serviceAccountUser", "Developer", "Deploy Cloud Run as the SA"])
    pdf.ln(3)

    pdf.h2("10.4  Key Commands Reference")
    pdf.code_block("""\
  # Auth (run once per machine)
  gcloud auth login
  gcloud auth application-default login
  gcloud config set project peq-tools

  # Verify auth works
  gcloud auth list
  gcloud auth application-default print-access-token > /dev/null && echo "ADC OK"

  # Local dev
  make install && cp .env.example .env && make dev
  curl -s localhost:8080/health | python -m json.tool
  curl -s localhost:8080/ready  | python -m json.tool

  # CI simulation (same as GitHub Actions)
  make lint && make test

  # Terraform (admin)
  cd infra/terraform && terraform init && terraform plan && terraform apply

  # Deploy
  make deploy && make smoke

  # Check no SA keys exist (zero-keys audit)
  for sa in $(gcloud iam service-accounts list --format='value(email)'); do
    echo "=== $sa ===" && gcloud iam service-accounts keys list --iam-account="$sa"
  done""", label="Essential commands")

    pdf.divider()
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GREY_LIGHT)
    pdf.multi_cell(
        0, 5,
        "Generated from the live tools-gcp repository -- June 2026.\n"
        "For the latest runbook steps, consult docs/CLONE_TO_RUNNING.md in the repository.",
        align="C",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
