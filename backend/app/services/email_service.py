import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


class EmailService:
    def __init__(self) -> None:
        self.host = os.getenv("SMTP_HOST", "")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM", self.username or "no-reply@codegym.local")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    @property
    def configured(self) -> bool:
        return bool(self.host and self.from_email)

    def send(self, to: str, subject: str, body: str) -> bool:
        if not self.configured:
            print(f"[DEV EMAIL] To: {to}\nSubject: {subject}\n{body}")
            return False

        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=15) as server:
            if self.use_tls:
                server.starttls()
            if self.username:
                server.login(self.username, self.password)
            server.send_message(message)
        return True


email_service = EmailService()
