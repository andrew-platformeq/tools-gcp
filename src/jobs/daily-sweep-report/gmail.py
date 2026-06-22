"""Gmail SMTP delivery for the daily sweep report."""

from __future__ import annotations

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import certifi
from daily_sweep_report.config import ReportSecrets

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def send_report_email(html: str, subject: str, secrets: ReportSecrets) -> None:
    """Send the HTML report via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = secrets.gmail_address
    msg["To"] = secrets.send_to
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=_SSL_CONTEXT) as server:
        server.login(secrets.gmail_address, secrets.gmail_app_password)
        server.sendmail(secrets.gmail_address, secrets.send_to, msg.as_string())
