from .. import models
from typing import Sequence
from . import user_crud
from pydantic import PositiveInt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class PermCrud:
    @staticmethod
    async def get_by_user_id(
        db: AsyncSession, user_id: PositiveInt
    ) -> Sequence[models.Perm] | None:
        try:
            user = await user_crud.UserCrud.get_by_id(
                db=db, id=user_id, load_perms=True
            )

            if not user:
                return None

            return user.grupo.permissoes
        except SQLAlchemyError as e:
            raise e
