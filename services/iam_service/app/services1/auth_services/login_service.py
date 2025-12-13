from loguru import logger
from fastapi import HTTPException, status
from app.domain.models import User
from app.domain.token_schemas import TokenSchema
from app.domain.user_schemas import UserLoginSchema
from app.services1.auth_services.hash_service import HashService
from app.services1.base_service import BaseService
from app.services1.user_service import UserService
from app.services1.auth_services.jwt_service import JWTService

class LoginService(BaseService):
    def __init__(
        self,
        user_service: UserService,
        hash_service: HashService,
        jwt_service: JWTService,
    ) -> None:
        super().__init__()
        self.user_service = user_service
        self.hash_service = hash_service
        self.jwt_service = jwt_service

    async def authenticate_user(self, user: UserLoginSchema) -> TokenSchema:
        # 1) پیدا کردن کاربر بر اساس ایمیل
        existing_user = await self.user_service.get_user_by_email(user.email)
        logger.info(f"Authenticating user with email {user.email}")

        # 2) اگر کاربر وجود نداشت → خطا
        if not existing_user:
            logger.error(f"User with email {user.email} does not exist")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not exist"
            )

        # 3) اگر کاربر هنوز verify نشده بود → خطا
        if not existing_user.is_verified:
            logger.error(f"User with email {user.email} is not verified")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not verified"
            )

        # 4) چک کردن پسورد
        if not self.hash_service.verify_password(
            user.password,
            existing_user.password_hash
        ):
            logger.error(f"Invalid password for user email {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # آپدیت آخرین ورود
        await self.user_service.update_last_login(existing_user.user_id)

        # 5) ساخت access_token
        access_token = self.jwt_service.create_access_token(
             str(existing_user.user_id)
        )
        # 5) ساخت refresh_token

        refresh_token = self.jwt_service.create_refresh_token( str(existing_user.user_id))


        logger.info(f"User with email {user.email} authenticated successfully")

        # 6) برگرداندن اسکیمای نهایی
        return {
       "access_token": access_token,
       "refresh_token": refresh_token,
       "token_type": "bearer"
               }