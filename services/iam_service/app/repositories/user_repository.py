from typing import Optional, List
from uuid import UUID
from datetime import datetime

from loguru import logger
from sqlalchemy import select, update ,delete
from sqlalchemy.ext.asyncio import AsyncSession

from services.iam_service.app.domain.models import User


class UserRepository:

    def __init__(self, session: AsyncSession):  #یعنی هر request یک session جدا دارد.
        self.session = session

    # -----------------------------------
    # CREATE
    # -----------------------------------
    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"User {user.user_id} created")
        return user


    # -----------------------------------
    # READ
    # -----------------------------------
    async def get_by_id(self, user_id: UUID) ->User:
        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        logger.info(f"Fetching user {user_id}")
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) ->User:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:#VALIDATION
        stmt = select(User.user_id).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def list_all(self) -> List[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # -----------------------------------
    # UPDATE
    # -----------------------------------
    async def update_last_login(self, user_id: UUID) -> None:
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(last_login=datetime)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_password(self, user_id: UUID, new_hash: str) -> None:
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                hashed_password=new_hash,
                updated_at=datetime
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    # -----------------------------------
    # VERIFY ACCOUNT
    # -----------------------------------
    async def verify_user(self, user_id: UUID) -> None:
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                is_verified=True,
                updated_at=datetime
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    # -----------------------------------
    # STATUS CHANGES
    # -----------------------------------
    async def set_status(self, user_id: UUID, status: str) -> None:
        """
        status must be: active | inactive | suspended
        """
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                status=status,
                updated_at=datetime
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def suspend_user(self, user_id: UUID) -> None:
        await self.set_status(user_id, "suspended")

    async def deactivate_user(self, user_id: UUID) -> None:
        await self.set_status(user_id, "inactive")

    async def activate_user(self, user_id: UUID) -> None:
        await self.set_status(user_id, "active")



    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()
        logger.info(f"User {user.user_id} deleted")


    async def get_user(self, user_id: UUID) -> User:
        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
# ---------------------------------------
# DEPENDENCY (برای FastAPI)
# ---------------------------------------
async def get_user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)




