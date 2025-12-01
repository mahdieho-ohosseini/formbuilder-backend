from uuid import UUID
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from services.iam_service.app.domain.models import User
from services.iam_service.app.core.database import get_db


class UserRepository:
    """
    Async User Repository for IAM Service
    Handles all DB operations for the users table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------------------------------------------
    # Create User
    # ---------------------------------------------------
    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # ---------------------------------------------------
    # Get User by Email
    # ---------------------------------------------------
    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ---------------------------------------------------
    # Get User by ID
    # ---------------------------------------------------
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ---------------------------------------------------
    # Check Exists (Email)
    # ---------------------------------------------------
    async def exists_by_email(self, email: str) -> bool:
        user = await self.get_user_by_email(email)
        return user is not None

    # ---------------------------------------------------
    # Update Last Login
    # ---------------------------------------------------
    async def update_last_login(self, user_id: UUID) -> None:
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(last_login="NOW()")
        )
        await self.session.execute(stmt)
        await self.session.commit()

    # ---------------------------------------------------
    # Save (Generic Update)
    # ---------------------------------------------------
    async def save(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


# -------------------------------------------------------
# FastAPI Dependency
# -------------------------------------------------------
async def get_user_repository(session: AsyncSession = None):
    """
    Injects a UserRepository instance using FastAPI Depends(get_db)
    """
    if session is None:
        # dynamically pull a session through get_db() generator
        async for db in get_db():
            session = db
            break

    yield UserRepository(session)
