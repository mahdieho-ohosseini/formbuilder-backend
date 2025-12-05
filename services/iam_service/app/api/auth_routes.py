import redis.asyncio as redis
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
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

# Services & Repositories
from app.repositories.user_repository import UserRepository
from app.services1.user_service import UserService
from app.services1.auth_services.signup_service import RegisterService
from app.services1.auth_services.login_service import LoginService
from app.services1.auth_services.jwt_service import JWTService
from app.services1.auth_services.otp_servise import OTPService
from app.services1.auth_services.hash_service import HashService
from app.services1.auth_services.email_service import EmailService

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication & Registration"]
)

# ===================================================================
# Dependency Injection Factories (حیاتی برای رفع ارور DI)
# ===================================================================

async def get_redis_client() -> redis.Redis:
    # تنظیمات اتصال به ردیس (می‌تونی از env بخونی)
    return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_hash_service() -> HashService:
    return HashService()

def get_jwt_service() -> JWTService:
    return JWTService()

def get_email_service() -> EmailService:
    return EmailService()

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
    hash_service: HashService = Depends(get_hash_service)
) -> UserService:
    return UserService(repo, hash_service)

async def get_otp_service(
    redis_client: redis.Redis = Depends(get_redis_client),
    email_service: EmailService = Depends(get_email_service)
) -> OTPService:
    return OTPService(redis_client, email_service)

# --- Factory اصلی برای RegisterService ---
async def get_register_service(
    user_service: UserService = Depends(get_user_service),
    otp_service: OTPService = Depends(get_otp_service),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> RegisterService:
    # این خط مشکل Missing Argument را حل می‌کند
    return RegisterService(user_service, otp_service, redis_client)

# --- Factory اصلی برای LoginService ---
async def get_login_service(
    user_service: UserService = Depends(get_user_service),
    hash_service: HashService = Depends(get_hash_service),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> LoginService:
    return LoginService(user_service, hash_service, jwt_service)

# --- Dependency برای گرفتن کاربر لاگین شده ---
async def get_current_user(
    token: str = Depends(JWTService.oauth2_scheme), 
    user_service: UserService = Depends(get_user_service),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> User:
    return await jwt_service.get_current_user(token, user_service)


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
    "/token",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    login_service: Annotated[LoginService, Depends(get_login_service)],
):
    logger.info(f"Logging in user with email: {form_data.username}")

    login_schema = UserLoginSchema(
        email=form_data.username,
        password=form_data.password
    )
    return await login_service.authenticate_user(login_schema)


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
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponseSchema:
    logger.info(f"Fetching details for user: {current_user.email}")
    return current_user
