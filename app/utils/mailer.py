import smtplib
from email.message import EmailMessage
from app.config import settings
from typing import Optional


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email using SMTP settings from config. Returns True on success."""
    if not settings.EMAIL_HOST or not settings.EMAIL_USERNAME or not settings.EMAIL_PASSWORD:
        # Email not configured
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg.set_content(body)

    try:
        if settings.EMAIL_USE_TLS:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)

        server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False
