from services.iam_service.app.services1.auth_services.email_service import EmailService

service = EmailService()

service.send_email(
    to_email="zrastgoo02@gmail.com",
    subject="Test from IAM Service",
    body="سلام عشقم! این یک تست ارسال ایمیل ازformly هست 🧪🔥"
)

print("Email sent!")
