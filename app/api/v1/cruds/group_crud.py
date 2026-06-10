from .. import models
from pydantic import PositiveInt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession


class GroupCrud:
    @staticmethod
    async def get_by_id(db: AsyncSession, id: PositiveInt) -> models.Group | None:
        try:
            stmt = (
                select(models.Group)
                .where(models.Group.id == id)
                .options(selectinload(models.Group.permissoes))
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise e
