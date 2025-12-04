from typing import Annotated
from loguru import logger
from fastapi import Depends, HTTPException, status

from app.domain.user_schemas import (
    UserCreateSchema,
    UserResponseSchema,
    UserCreateResponseSchema,
    VerifyOTPSchema,
    VerifyOTPResponseSchema,
    ResendOTPSchema,
    ResendOTPResponseSchema,
)
from app.services1.auth_services.otp_servise import OTPService
from app.services1.base_service import BaseService
from app.services1.user_service import UserService


class RegisterService(BaseService):
    def __init__(
        self,
        user_service: Annotated[UserService, Depends()],
        otp_service: Annotated[OTPService, Depends()],
    ) -> None:
        super().__init__()

        self.user_service = user_service
        self.otp_service = otp_service
        

    # ============================================================
    # Register user (Email-based)
    # ============================================================
    async def register_user(self, user: UserCreateSchema) -> UserCreateResponseSchema:

        # 1. Check duplicate email
        existing = await self.user_service.get_user_by_email(user.email)
        if existing:
            logger.error(f"User with email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User already exists"
            )

        # 2. Create user
        new_user = await self.user_service.create_user(user)

        # 3. Send OTP to email
        otp = self.otp_service.send_otp(new_user.email)

        logger.info(f"User with email {user.email} created successfully")

        return UserCreateResponseSchema(
            user=UserResponseSchema.from_orm(new_user),
            OTP=otp,
            message="User created successfully. OTP sent to email",
        )

    # ============================================================
    # Verify user using OTP (Email-based)
    # ============================================================
    async def verify_user(
        self, verify_schema: VerifyOTPSchema
    ) -> VerifyOTPResponseSchema:

        email = verify_schema.email

        # 1. Verify OTP
        if not self.otp_service.verify_otp(email, verify_schema.OTP):
            logger.error(f"Invalid OTP for email {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
            )

        # 2. Find user
        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )

        # 3. Mark as verified
        await self.user_service.update_user(
            user.user_id, {"is_verified": True}
        )

        logger.info(f"User with email {email} verified")

        return VerifyOTPResponseSchema(
            verified=True, message="User verified successfully"
        )

    # ============================================================
    # Resend OTP (Email-based)
    # ============================================================
    async def resend_otp(
        self, resend_schema: ResendOTPSchema
    ) -> ResendOTPResponseSchema:

        email = resend_schema.email

        user = await self.user_service.get_user_by_email(email)
        if not user:
            logger.error(f"User with email {email} does not exist")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User does not exist"
            )

        if user.is_verified:
            logger.error(f"User with email {email} already verified")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User already verified"
            )

        # If OTP already exists (not expired)
        if self.otp_service.check_exist(email):
            logger.error(f"OTP for email {email} already active")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="OTP already exists"
            )

        otp = self.otp_service.send_otp(email)

        logger.info(f"OTP resent to email {email}")

        return ResendOTPResponseSchema(
            email=email,
            OTP=otp,
            message="OTP sent to email",
        )
