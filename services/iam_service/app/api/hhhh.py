from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.domain.models import User
from loguru import logger


class UserRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

 
    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"User {user.id} created")
        return user

    async def update_user(self, user_id: int, updated_user: Dict) -> User:
        # Update user with the given id
        user_query = self.db.query(User).filter(User.id == user_id)
        db_user = user_query.first()
        user_query.filter(User.id == user_id).update(
            updated_user, synchronize_session=False
        )
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"User {user_id} updated")
        return 
    

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
        self.db.flush()
        logger.info(f"User {user.id} deleted")

    def get_user(self, user_id: UUID) -> User:
        logger.info(f"Fetching user {user_id}")
        return self.db.get(User, user_id)

    def get_user_by_mobile_number(self, mobile_number: str) -> User:
        logger.info(f"Fetching user with mobile number {mobile_number}")
        return self.db.query(User).filter(User.mobile_number == mobile_number).first()
       
