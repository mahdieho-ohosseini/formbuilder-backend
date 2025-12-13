from typing import Annotated, Dict
from uuid import UUID
from loguru import logger
from fastapi import Depends
from datetime import datetime
from typing import Optional

from app.domain.models import User
from app.domain.user_schemas import UserCreateSchema
from app.repositories.user_repository import UserRepository
from app.services1.auth_services.hash_service import HashService
from app.services1.base_service import BaseService
from app.repositories.RefreshTokenRepository import RefreshTokenRepository

class UserService(BaseService):
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
        hash_service: HashService = Depends(),
        refresh_token_repository: Optional[RefreshTokenRepository] = None,    ) -> None:
        super().__init__()
        self.user_repository = user_repository
        self.hash_service = hash_service
        self.refresh_token_repository = refresh_token_repository  # ✅

    async def create_user(self, user_body: UserCreateSchema) -> User:
        logger.info(f"Creating user with email {user_body.email}")
        password_hash = self.hash_service.hash_password(user_body.password)

        user_model = User(
            full_name=user_body.full_name,
            email=user_body.email,
            password_hash=password_hash,
            role="creator",
            is_verified=True,
        )

        return await self.user_repository.create_user(user_model)

    async def update_full_name(self, user_id: UUID, new_full_name: str) -> None:
        logger.info(f"Updating full_name for user {user_id}")
        await self.user_repository.update_full_name(user_id, new_full_name)

    async def update_password(self, user_id: UUID, new_password_hash: str) -> None:
        logger.info(f"Updating password for user {user_id}")
        hashed = self.hash_service.hash_password(new_password_hash)
        await self.user_repository.update_password(user_id, hashed)

    async def delete_user(self, user: User) -> None:
        logger.info(f"Deleting user with id {user.user_id}")
        return await self.user_repository.delete_user(user)

    async def get_user(self, user_id: UUID) -> User:
        logger.info(f"Fetching user with id {user_id}")
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User:
        logger.info(f"Fetching user with email {email}")
        return await self.user_repository.get_by_email(email)

    async def update_last_login(self, user_id: UUID):
        return await self.user_repository.update_last_login(user_id)
    

    async def invalidate_all_tokens(self, user_id: UUID):
     """Invalidate all refresh tokens (only if repository is available)"""
     if self.refresh_token_repository is None:
        logger.warning(
            f"Cannot invalidate tokens for user {user_id}: RefreshTokenRepository not injected"
        )
        return
    
     await self.refresh_token_repository.delete_all_by_user_id(user_id)



    async def create_admin(self, user_body: UserCreateSchema) -> User:
        logger.info("Creating admin user")
        
        existing_admin = await self.user_repository.get_admin_user()
        if existing_admin:
            raise ValueError("An admin user already exists")

        hashed = self.hash_service.hash_password(user_body.password)

        admin_user = User(
            full_name=user_body.full_name,
            email=user_body.email,
            password_hash=hashed,
            role="admin",
            is_verified=True,
        )

        return await self.user_repository.create_user(admin_user)
