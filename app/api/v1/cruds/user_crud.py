from .. import models
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import PositiveInt, EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class UserCrud:
    @staticmethod
    async def get_by_email(
        db: AsyncSession, email: EmailStr, load_perms: bool = False
    ) -> models.User | None:
        try:
            stmt = select(models.User).where(models.User.email == email)

            if load_perms:
                stmt = stmt.options(
                    selectinload(models.User.grupo).selectinload(
                        models.Group.permissoes
                    )
                )
            else:
                stmt = stmt.options(selectinload(models.User.grupo))

            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise e

    @staticmethod
    async def get_by_id(
        db: AsyncSession, id: PositiveInt, load_perms: bool = False
    ) -> models.User | None:
        try:
            stmt = select(models.User).where(models.User.id == id)

            if load_perms:
                stmt = stmt.options(
                    selectinload(models.User.grupo).selectinload(
                        models.Group.permissoes
                    )
                )
            else:
                stmt = stmt.options(selectinload(models.User.grupo))

            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise e
