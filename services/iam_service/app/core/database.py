from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import declarative_base
from loguru import logger
from sqlalchemy import text


from services.iam_service.app.core.config import get_settings

config = get_settings()

# ساخت URL مخصوص asyncpg
DATABASE_URL = (
    f"postgresql+asyncpg://{config.DATABASE_USERNAME}:"
    f"{config.DATABASE_PASSWORD}@{config.DATABASE_HOSTNAME}:"
    f"{config.DATABASE_PORT}/{config.DATABASE_NAME}"
)

# ساخت async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=config.DEBUG_MODE,
    future=True
)

# Session factory
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession
)

# Base برای تمام مدل‌های دیتابیس
EntityBase = declarative_base()


# Dependency برای FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception as ex:
            logger.error(f"DB error: {ex}")
            await session.rollback()
            raise
        finally:
            await session.close()
# ================================================
# Database Health Check
# ================================================
async def db_health_check() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as ex:
        logger.error(f"[DB Health] Connection Error: {ex}")
        return False
