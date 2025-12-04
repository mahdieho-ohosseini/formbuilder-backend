from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from loguru import logger

from app.domain.models import User
from app.domain.token_schemas import TokenSchema
from app.domain.user_schemas import (
    UserCreateSchema,
    UserCreateResponseSchema,
    UserResponseSchema,
    UserLoginSchema,
    VerifyOTPSchema,
    VerifyOTPResponseSchema,
    ResendOTPSchema,
    ResendOTPResponseSchema,
)
from app.services1.auth_services.login_service import loginService
from app.services1.auth_services.jwt_service import JWTService  # مسیر get_current_user را به‌روز کنید
from app.services1.auth_services.signup_service import RegisterService

# ===================================================================
# APIRouter Configuration
# ===================================================================
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication & Registration"]
)


# ===================================================================
# 1. Register Endpoint
# ===================================================================
@auth_router.post(
    "/register",  # نام مسیر استاندارد (lowercase)
    response_model=UserCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user with email"
)
async def register(
    user_data: UserCreateSchema,
    register_service: Annotated[RegisterService, Depends()]
) -> UserCreateResponseSchema:
    # لاگ اصلاح شد تا بر اساس ایمیل باشد
    logger.info(f"Registering user with email: {user_data.email}")
    return await register_service.register_user(user_data)


# ===================================================================
# 2. Login Endpoint (Get Token)
# ===================================================================
@auth_router.post(
    "/token",  # نام مسیر استاندارد
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
    summary="Login for access token"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    login_service: Annotated[loginService, Depends()],
) -> TokenSchema:
    # لاگ اصلاح شد: form_data.username همان ایمیل است
    logger.info(f"Logging in user with email: {form_data.username}")

    # **مهم‌ترین اصلاح**: UserLoginSchema باید با email ساخته شود، نه mobile_number
    login_schema = UserLoginSchema(
        email=form_data.username,
        password=form_data.password
    )
    return await login_service.authenticate_user(login_schema)


# ===================================================================
# 3. Verify OTP Endpoint
# ===================================================================
@auth_router.post(
    "/verify-otp",  # نام مسیر استاندارد
    response_model=VerifyOTPResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verify user account with OTP"
)
async def verify_otp(
    verify_schema: VerifyOTPSchema,
    register_service: Annotated[RegisterService, Depends()],
) -> VerifyOTPResponseSchema:
    # لاگ اصلاح شد تا بر اساس ایمیل باشد
    logger.info(f"Verifying OTP for user with email: {verify_schema.email}")
    return await register_service.verify_user(verify_schema)


# ===================================================================
# 4. Resend OTP Endpoint
# ===================================================================
@auth_router.post(
    "/resend-otp",  # نام مسیر استاندارد
    response_model=ResendOTPResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Resend OTP to user's email"
)
async def resend_otp(
    resend_schema: ResendOTPSchema,
    register_service: Annotated[RegisterService, Depends()],
) -> ResendOTPResponseSchema:
    # لاگ اصلاح شد تا بر اساس ایمیل باشد
    logger.info(f"Resending OTP for user with email: {resend_schema.email}")
    return await register_service.resend_otp(resend_schema)


# ===================================================================
# 5. Get Current User Endpoint
# ===================================================================
@auth_router.get(
    "/me",  # نام مسیر استاندارد
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user's details"
)
async def read_users_me(
    current_user: Annotated[User, Depends(JWTService.get_current_user)]
) -> UserResponseSchema:
    # لاگ اصلاح شد تا بر اساس ایمیل باشد
    logger.info(f"Fetching details for user: {current_user.email}")
    return current_user
