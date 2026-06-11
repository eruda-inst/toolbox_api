from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.token_blacklist_model import TokenBlacklist


class CleanupService:
    @staticmethod
    async def del_expired_blacklist_tokens(db: AsyncSession) -> None:
        now = datetime.now(ZoneInfo("America/Bahia"))
        stmt = delete(TokenBlacklist).where(TokenBlacklist.expiracao < now)
        await db.execute(stmt)
        await db.commit()
