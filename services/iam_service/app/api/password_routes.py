from typing import Annotated
from fastapi import APIRouter, Depends

from app.domain.resetpass_schemas import (
    PasswordResetResendSchema,
    PasswordResetStartSchema,
    PasswordResetVerifySchema,
    PasswordResetCompleteSchema,
    PasswordResetResponseSchema,
)
from app.services1.auth_services.password_reset_service import PasswordResetService
from app.dependencies import get_password_reset_service

router = APIRouter(
    prefix="/auth/password-reset",
    tags=["Auth"],
)

# -----------------------------
# 1️⃣ Start Password Reset
# -----------------------------
@router.post("/start", response_model=PasswordResetResponseSchema)
async def start_password_reset(
    data: PasswordResetStartSchema,
    service: PasswordResetService = Depends(get_password_reset_service),  # ✅
):
    return await service.start(data.email)


# -----------------------------
# 2️⃣ Verify OTP
# -----------------------------
@router.post("/verify", response_model=PasswordResetResponseSchema)
async def verify_password_reset(
    data: PasswordResetVerifySchema,
    service: PasswordResetService = Depends(get_password_reset_service),  # ✅ تصحیح شد
):
    return await service.verify(data.email, data.otp)


# -----------------------------
# 3️⃣ Complete Passwod Reset
# -----------------------------
@router.post("/complete", response_model=PasswordResetResponseSchema)
async def complete_password_reset(
    data: PasswordResetCompleteSchema,
    service: PasswordResetService = Depends(get_password_reset_service),  # ✅ تصحیح شد
):
    return await service.complete(data.email, data.new_password)


@router.post("/resend_otp", response_model=None)
async def resend_password_reset_otp(
    data: PasswordResetResendSchema,
service: PasswordResetService = Depends(get_password_reset_service),
):
    return await service.resend(data.email)
