import asyncio
from services.iam_service.app.repositories .user_repository import UserRepository
from services.iam_service.app.domain.models import User
from services.iam_service.app.core.database import async_session


async def main():
    async with async_session() as session:
        repo = UserRepository(session)

        # Create user
        user = user(
            email="test@example.com",
            password_hash="hashedpass123",
            full_name="Test User",
            role="creator",
        )
        created = await repo.create_user(user)
        print("Created:", created.user_id)

        # Fetch by email
        fetched = await repo.get_user_by_email("test@example.com")
        print("Fetched:", fetched.full_name)

        # Exists check
        print("Exists:", await repo.exists_by_email("test@example.com"))

        # Update last login
        await repo.update_last_login(created.user_id)
        print("Last login updated.")

asyncio.run(main())
