"""
Sends the report email via Gmail SMTP.
Requires a Gmail App Password (not your regular password).
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_report(
    subject: str,
    text_body: str,
    html_body: str,
) -> None:
    """
    Send the report via Gmail SMTP.

    Required env vars:
        GMAIL_ADDRESS      — your Gmail address, e.g. "you@gmail.com"
        GMAIL_APP_PASSWORD — 16-char app password from Google account settings
        EMAIL_TO           — recipient address (can be the same as GMAIL_ADDRESS)
    """
    gmail_address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipients = [r.strip() for r in os.environ["EMAIL_TO"].split(",")]

    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_address
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, recipients, msg.as_string())

    print(f"Email sent to {', '.join(recipients)}")
