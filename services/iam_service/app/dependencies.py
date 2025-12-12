from typing import Annotated
from fastapi import Depends
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


bearer_scheme = HTTPBearer()


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
    hash_service: HashService = Depends(get_hash_service)
) -> UserService:
    return UserService(repo, hash_service)

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
    user_service: UserService = Depends(get_user_service)
) -> JWTService:
    return JWTService(user_service)


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
    jwt_service: JWTService = Depends(get_jwt_service)
):
    token = credentials.credentials
    return await jwt_service.get_current_user(token)
