from datetime import datetime, timedelta
import jwt

from app.services1.user_service import UserService
from app.services1.base_service import BaseService
from app.domain.models import User
SECRET_KEY = "your-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class JWTService(BaseService):
    def __init__(self, user_service: UserService) -> None:
        super().__init__()
        self.user_service = user_service

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def decode_token(self, token: str) -> dict:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    async def get_current_user(self, token: str) -> User:
        data = await self.decode_token(token)
        user_id = data.get("sub")
        if user_id is None:
            raise Exception("Invalid token")
        return await self.user_service.get_user(user_id)
