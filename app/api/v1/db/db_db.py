from .. import cores
from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

database_url = cores.settings.database_url

engine = create_async_engine(
    url=database_url,
    future=True,
    pool_pre_ping=True,  # Test the connection (SELECT 1) before delivering it to the session.
    pool_recycle=1800,  # Recycles connections every 30 minutes (1800 seconds) to prevent database timeouts.
)

SessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
