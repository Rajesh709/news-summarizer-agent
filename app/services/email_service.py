import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    """Sends HTML emails via Gmail SMTP."""

    def __init__(self) -> None:
        settings = get_settings()
        self._sender = settings.email_sender
        self._password = settings.email_app_password
        self._smtp_host = settings.smtp_host
        self._smtp_port = settings.smtp_port

    def send(self, to: str, subject: str, html_body: str) -> bool:
        """Send an HTML email. Returns True on success."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"NewsBot AI 📰 <{self._sender}>"
            msg["To"] = to
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP_SSL(self._smtp_host, self._smtp_port) as server:
                server.login(self._sender, self._password)
                server.sendmail(self._sender, to, msg.as_string())

            logger.info("email_sent", to=to, subject=subject)
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("email_auth_error", hint="Check Gmail App Password in .env")
            return False
        except Exception as exc:
            logger.error("email_send_error", error=str(exc))
            return False
