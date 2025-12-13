from typing import Annotated
from argon2 import hash_password
from fastapi import Depends, HTTPException
from app.services1.auth_services.otp_service import OTPService
from app.services1.user_service import UserService
from app.core.redis import get_redis_client
from app.services1.auth_services.hash_service import HashService

class PasswordResetService:
    def __init__(
        self,
        user_service: Annotated[UserService, Depends()],
        otp_service: Annotated[OTPService, Depends()],
        redis_client: Annotated[any, Depends(get_redis_client)],
    ):
        self.user_service = user_service
        self.otp_service = otp_service
        self.redis = redis_client

    async def start(self, email: str):
        user = await self.user_service.get_user_by_email(email)

        # همیشه پاسخ یکسان → جلوگیری از user enumeration
        if user:
            await self.otp_service.send_otp(email)

        return {"success": True, "message": "If email exists, OTP sent"}
    async def verify(self, email: str, otp: str):
        valid = await self.otp_service.verify_otp(email, otp)
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # create reset session
        await self.redis.setex(
            f"reset_session:{email}",
            600,
            "1"
        )

        return {"success": True, "message": "OTP verified"}
    async def complete(self, email: str, new_password: str):
        exists = await self.redis.exists(f"reset_session:{email}")
        if not exists:
            raise HTTPException(status_code=403, detail="Reset session expired")

        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        user.password = hash_password(new_password)
        await self.user_service.save(user)

        # cleanup
        await self.redis.delete(f"reset_session:{email}")

        # ⛔ invalidate refresh tokens (تو داری)
        await self.user_service.invalidate_all_tokens(user.id)

        return {"success": True, "message": "Password reset successful"}



