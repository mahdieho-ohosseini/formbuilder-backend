from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr
from app.domain.token_schemas import TokenSchema



class UserBaseSchema(BaseModel):
    full_name: str
    email :EmailStr

class UserCreateSchema(UserBaseSchema):
    password: str


class UserLoginSchema(BaseModel):
    email :EmailStr
    password: str


class UserResponseSchema(UserBaseSchema):
    id: UUID
    role: str
    created_at: Optional[datetime]
    is_verified: bool

    class Config:
        from_attributes = True


class VerifyOTPSchema(BaseModel):#ورودی کاربر
    email :EmailStr 
    OTP: str



class ResendOTPSchema(BaseModel):
    email :EmailStr


class ResendOTPResponseSchema(BaseModel):
    message: str
    success: bool

class VerifyOTPResponseSchema(BaseModel):#پاسخ موفقیت اعتبارسنجی بهه کاربر  خروچی تایید otp
    verified: bool
    message: str


class UserCreateResponseSchema(BaseModel):
    user: UserResponseSchema
    message: str
    success: bool


class UserLoginResponseSchema(BaseModel):
    user: UserResponseSchema
    access_token: TokenSchema
