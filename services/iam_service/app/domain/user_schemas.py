from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

# ======================================================
# Base User Schemas
# ======================================================

class UserBaseSchema(BaseModel):
    full_name: str
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    password: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    user_id: UUID
    full_name: str
    email: EmailStr
    role: str
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    is_verified: bool

    class Config:
        from_attributes = True


# ======================================================
# OTP-Based Registration (Hybrid Architecture)
# ======================================================

# مرحله ۱ — فقط ارسال OTP
class RegisterStartResponse(BaseModel):
    success: bool
    message: str


# مرحله ۲ — تأیید OTP و ساخت کاربر
class RegisterCompleteSchema(BaseModel):
    email: EmailStr
    otp: str   # مهم: otp با حروف کوچک


class RegisterCompleteResponse(BaseModel):
    success: bool
    verified: bool
    message: str
    user: UserResponseSchema


# ======================================================
# Resend OTP
# ======================================================

class ResendOTPSchema(BaseModel):
    email: EmailStr


class ResendOTPResponseSchema(BaseModel):
    success: bool
    message: str
