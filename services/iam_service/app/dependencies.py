from typing import Annotated, Any
from fastapi import Depends, HTTPException
import redis.asyncio as redis

# Core
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

# Repositories
from app.repositories.user_repository import UserRepository

# Services
from app.services1.auth_services.hash_service import HashService
from app.services1.user_service import UserService
from app.services1.auth_services.jwt_service import JWTService
from app.services1.auth_services.login_service import LoginService
from app.services1.auth_services.signup_service import RegisterService
from app.services1.auth_services.otp_service import OTPService
from app.services1.auth_services.email_service import EmailService

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services1.auth_services.password_reset_service import PasswordResetService
from app.repositories.RefreshTokenRepository import RefreshTokenRepository
from app.services1.profile_service import ProfileService


bearer_scheme = HTTPBearer()
async def get_refresh_token_repository(
    db: AsyncSession = Depends(get_db)
) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


# -----------------------------
# Redis + Hash + Email
# -----------------------------
async def get_redis_client() -> redis.Redis:
    return redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

def get_hash_service() -> HashService:
    return HashService()


def get_email_service() -> EmailService:
    return EmailService()


# -----------------------------
# Repository Factory
# -----------------------------
async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(db)


# -----------------------------
# UserService Factory
# -----------------------------
async def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
    hash_service: HashService = Depends(get_hash_service),
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository)  # ✅ این خط رو اضافه کن
) -> UserService:
    return UserService(repo, hash_service, refresh_token_repo)  # ✅ اینجا هم

# -----------------------------
# OTP Service
# -----------------------------
async def get_otp_service(
    redis_client: redis.Redis = Depends(get_redis_client),
    email_service: EmailService = Depends(get_email_service)
) -> OTPService:
    return OTPService(redis_client, email_service)


# -----------------------------
# JWT
# -----------------------------
def get_jwt_service(
    jwt_service: JWTService = Depends(),
) -> JWTService:
    return jwt_service

# -----------------------------
# Register Service
# -----------------------------
async def get_register_service(
    user_service: UserService = Depends(get_user_service),
    otp_service: OTPService = Depends(get_otp_service),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> RegisterService:
    return RegisterService(user_service, otp_service, redis_client)


# -----------------------------
# Login Service
# -----------------------------
def get_login_service(
    user_service: UserService = Depends(get_user_service),
    hash_service: HashService = Depends(get_hash_service),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    return LoginService(
        user_service,
        hash_service,
        jwt_service
    )

# -----------------------------
# Get current user
# -----------------------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_user_service),
):
    token = credentials.credentials

    payload = await jwt_service.decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
#-----------------------------------------
# در dependencies.py
async def get_password_reset_service(
    user_service: UserService = Depends(get_user_service),
    otp_service: OTPService = Depends(get_otp_service),
    redis_client: Any = Depends(get_redis_client),
    hash_service: HashService = Depends(get_hash_service)
) -> PasswordResetService:
    return PasswordResetService(
        user_service,
        otp_service,
        redis_client,
        hash_service
    )


async def get_profile_service(
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    hash_service: HashService = Depends(get_hash_service)
) -> ProfileService:
    return ProfileService(
        db=db,
        user_service=user_service,
        hash_service=hash_service
    )