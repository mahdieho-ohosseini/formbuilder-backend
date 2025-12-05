from datetime import datetime, timedelta, timezone
import jwt
from jwt import PyJWTError
from loguru import logger

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from app.services1.base_service import BaseService
from app.services1.user_service import UserService
from app.domain.models import User




class JWTService(BaseService):
    def __init__(self) -> None:
        super().__init__()
        self.secret_key = self.settings.JWT_SECRET_KEY
        self.algorithm = self.settings.JWT_ALGORITHM
        self.exp_minutes = self.settings.ACCESS_TOKEN_EXPIRE_MINUTES

        
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

    # ============================================================
    #  تابع اول: ساخت توکن
    # ============================================================
    def create_access_token(self, data: dict) -> str:
        logger.info("Creating access token")

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.exp_minutes)
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm,
        )

    # ============================================================
    #  تابع دوم: گرفتن کاربر فعلی
    # ============================================================
    async def get_current_user(
        self,
        token: Annotated[str, Depends(oauth2_scheme)],
        user_service: Annotated[UserService, Depends()],
    ) -> User:

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        logger.info(f"Validating token: {token}")

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

            user_id: str = payload.get("sub")
            if user_id is None:
                logger.error("Token missing 'sub'")
                raise credentials_exception

            user = await user_service.get_user(user_id)

        except PyJWTError:
            logger.error("Error decoding token")
            raise credentials_exception

        if user is None:
            logger.error("User not found")
            raise credentials_exception

        logger.info(f"User {user_id} authenticated")
        return user
