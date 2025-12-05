import smtplib
from email.mime.text import MIMEText
from fastapi import Depends
from app.services1.base_service import BaseService
from app.core.config import get_settings


class EmailService(BaseService):
    def __init__(self):
        super().__init__()
        self.settings = get_settings()

    async def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.settings.EMAIL_FROM
        msg["To"] = to_email

        # ارسال ایمیل با SMTP (sync → داخل executor)
        def _send():
            with smtplib.SMTP(self.settings.EMAIL_HOST, self.settings.EMAIL_PORT) as smtp:
                smtp.starttls()
                smtp.login(self.settings.EMAIL_USERNAME, self.settings.EMAIL_PASSWORD)
                smtp.sendmail(self.settings.EMAIL_FROM, [to_email], msg.as_string())

        # اجرای کد sync در threadpool
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)


# ================================
# Dependency Function (بیرون کلاس)
# ================================
def get_email_service():
    return EmailService()
