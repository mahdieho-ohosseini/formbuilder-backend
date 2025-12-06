import redis.asyncio as redis
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from loguru import logger

# ===================================================================
# Imports & Schemas
# ===================================================================
from app.core.database import get_db
from app.domain.models import User
from app.domain.token_schemas import TokenSchema
from app.domain.user_schemas import (
    UserCreateSchema,
    RegisterStartResponse,    # جدید برای معماری Hybrid (مرحله اول)
    RegisterCompleteSchema,   # جایگزین VerifyOTPSchema
    RegisterCompleteResponse, # جدید برای معماری Hybrid (مرحله دوم)
    UserLoginSchema,
    ResendOTPSchema,
    ResendOTPResponseSchema,
    UserResponseSchema
)
from app.dependencies import (
    get_register_service,
    get_login_service,
    get_user_service,
    get_jwt_service,
    get_hash_service,
)


# Services & Repositories
from app.repositories.user_repository import UserRepository
from app.services1.user_service import UserService
from app.services1.auth_services.signup_service import RegisterService
from app.services1.auth_services.login_service import LoginService
from app.services1.auth_services.jwt_service import JWTService
from app.services1.auth_services.otp_servise import OTPService
from app.services1.auth_services.hash_service import HashService
from app.services1.auth_services.email_service import EmailService
from app.services1.auth_services import jwt_service
from app.dependencies import get_current_user

bearer_scheme = HTTPBearer(auto_error=True)


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication & Registration"]
)

# ===================================================================
# Dependency Injection Factories (حیاتی برای رفع ارور DI)
# ===================================================================


# ===================================================================
# 1. Register Endpoint (Step 1: Send OTP)
# ===================================================================
@auth_router.post(
    "/register",
    response_model=RegisterStartResponse,  # تغییر به اسکیمای درست (بدون User Object)
    status_code=status.HTTP_200_OK,        # 200 چون هنوز Create نشده (Pending است)
    summary="Step 1: Submit email & password -> Receive OTP"
)
async def register(
    user_data: UserCreateSchema,
    register_service: Annotated[RegisterService, Depends(get_register_service)] # استفاده از Factory
):
    """
    دریافت ایمیل و پسورد -> ذخیره موقت در ردیس -> ارسال OTP
    """
    logger.info(f"Starting registration for email: {user_data.email}")
    return await register_service.register_user(user_data)


# ===================================================================
# 2. Verify OTP Endpoint (Step 2: Create User)
# ===================================================================
@auth_router.post(
    "/verify-otp",
    response_model=RegisterCompleteResponse, # تغییر به اسکیمای نهایی (User Created)
    status_code=status.HTTP_201_CREATED,
    summary="Step 2: Verify OTP -> Create User in DB"
)
async def verify_otp(
    verify_schema: RegisterCompleteSchema, # استفاده از اسکیمای جدید
    register_service: Annotated[RegisterService, Depends(get_register_service)]
):
    """
    تایید OTP -> خواندن اطلاعات از ردیس -> ساخت کاربر در دیتابیس
    """
    logger.info(f"Verifying OTP for user with email: {verify_schema.email}")
    return await register_service.verify_user(verify_schema)


# ===================================================================
# 3. Login Endpoint
# ===================================================================
@auth_router.post(
    "/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK
)
async def login(
    login_data: UserLoginSchema,
    login_service: Annotated[LoginService, Depends(get_login_service)]
):
    return await login_service.authenticate_user(login_data)

# ===================================================================
# 4. Resend OTP Endpoint
# ===================================================================
@auth_router.post(
    "/resend-otp",
    response_model=ResendOTPResponseSchema,
)
async def resend_otp(
    resend_schema: ResendOTPSchema,
    register_service: Annotated[RegisterService, Depends(get_register_service)],
):
    logger.info(f"Resending OTP for user with email: {resend_schema.email}")
    return await register_service.resend_otp(resend_schema)


# ===================================================================
# 5. Get Current User Endpoint
# ===================================================================
@auth_router.get(
    "/me",
    response_model=UserResponseSchema,
    dependencies=[Depends(bearer_scheme)],
    openapi_extra={"security": [{"BearerAuth": []}]},
    summary="Get current authenticated user",
)
async def me(current_user=Depends(get_current_user)):
    return current_user
