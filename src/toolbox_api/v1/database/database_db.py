from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .. import config

engine = create_async_engine(
    url=config.settings.database_url_async,
    future=True,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Summary.

    Returns:
        AsyncGenerator[AsyncSession, Any]: Description.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
