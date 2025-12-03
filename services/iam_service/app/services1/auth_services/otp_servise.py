import random
from typing import Annotated
from fastapi import Depends
from redis import Redis
from loguru import logger
from app.core.config import get_settings
from app.core.redis import get_redis
from app.services1.base_service import BaseService
from app.services1.auth_services.email_service import EmailService  

class OTPService(BaseService):
    def __init__(
        self,
        redis_client: Annotated[Redis, Depends(get_redis)],
        email_service: Annotated[EmailService, Depends(EmailService)]
    ) -> None:
        super().__init__()
        self.redis_client = redis_client
        self.email_service = email_service
        self.settings = get_settings()


    @staticmethod
    def __generate_otp() -> str:
        return str(random.randint(100000, 999999))


    def send_otp(self, email: str) -> str:
        otp = self.__generate_otp()

        # 1) ذخیره در Redis با expire
        self.redis_client.setex(email, self.settings.OTP_EXPIRE_TIME, otp)

        # 2) ارسال ایمیل
        subject = "Your OTP Code"
        message = f"Your verification code is: {otp}"
        self.email_service.send_email(email, subject, message)

        logger.info(f"OTP sent to email: {email}")
        return otp

    def verify_otp(self, email: str, otp: str) -> bool:
        stored_otp = self.redis_client.get(email)
        return stored_otp is not None and stored_otp == otp

    def check_exist(self, email: str) -> bool:
        return self.redis_client.get(email) is not None
