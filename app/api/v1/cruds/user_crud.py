from .. import models
from fastapi.logger import logger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCrud:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> models.User | None:
        try:
            stmt = (
                select(models.User)
                .where(models.User.email == email)
                .options(
                    selectinload(models.User.grupo).selectinload(
                        models.Group.permissoes
                    )
                )
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(e)
            raise e
