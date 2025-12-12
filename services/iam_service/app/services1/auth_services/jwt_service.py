from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, status # اضافه شد برای ارورهای تمیزتر

from app.services1.user_service import UserService
from app.services1.base_service import BaseService
from app.domain.models import User
from app.core.config import Settings

class JWTService(BaseService):
    def __init__(self, user_service: UserService) -> None:
        super().__init__()
        self.user_service = user_service

    # --- 1. تولید اکسس توکن (همون قبلی) ---
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # ما type رو اضافه می‌کنیم که کسی نتونه جای رفرش قالبش کنه
        to_encode.update({"exp": expire, "type": "access"}) 
        return jwt.encode(to_encode,Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)

    # --- 2. تولید رفرش توکن (جدید) ---
    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=Settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # تایپ رو refresh می‌ذاریم
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode,Settings.JWT_SECRET_KEY, algorithm=Settings.JWT_ALGORITHM)

    # --- 3. دیکود کردن (عمومی) ---
    async def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token,Settings.JWT_SECRET_KEY, algorithms=[Settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    # --- 4. گرفتن کاربر (برای میدل‌ور یا Depend) ---
    async def get_current_user(self, token: str) -> User:
        payload = await self.decode_token(token)
        
        # چک امنیتی: مطمئن شیم توکن Access هست نه Refresh
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type (expected access)")

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token subject")
            
        return await self.user_service.get_user(user_id)

    # --- 5. متد اصلی رفرش کردن (Magic Happens Here) ---
    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        رفرش توکن رو میگیره، اگه معتبر بود، یه اکسس توکن جدید میده.
        """
        payload = await self.decode_token(refresh_token)

        # 1. چک کنیم که واقعاً رفرش توکنه
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type (expected refresh)")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # 2. (اختیاری ولی توصیه شده) چک کنیم یوزر هنوز تو دیتابیس هست؟
        # user = await self.user_service.get_user(user_id)
        # if not user: ...

        # 3. صدور اکسس توکن جدید
        new_access_token = self.create_access_token({"sub": user_id})
        return new_access_token
