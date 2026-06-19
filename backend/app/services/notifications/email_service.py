import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "no-reply@lifeos-ai.com")

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Sends HTML email via SMTP or falls back to logger in local environments."""
    if not SMTP_USER or not SMTP_PASSWORD:
        # Development fallback
        print(f"[SMTP Fallback] Target: {to_email} | Subject: {subject}")
        print(f"[Body Content]: {html_content[:200]}...")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[SMTP Error] Failed to send email to {to_email}: {e}")
        return False
