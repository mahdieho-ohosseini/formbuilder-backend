import smtplib
from email.mime.text import MIMEText
from services.iam_service.app.services1.base_service import BaseService
from app.core.config import get_settings


class EmailService(BaseService):
    def __init__(self):
        super().__init__()
        self.settings = get_settings()


    def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.settings.EMAIL_FROM
        msg["To"] = to_email

        with smtplib.SMTP(self.settings.EMAIL_HOST, self.settings.EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(self.settings.EMAIL_USERNAME, self.settings.EMAIL_PASSWORD)
            smtp.sendmail(self.settings.EMAIL_FROM, [to_email], msg.as_string())
