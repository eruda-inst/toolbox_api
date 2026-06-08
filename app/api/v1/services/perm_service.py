from .. import schemas, cruds
from pydantic import PositiveInt
from fastapi.logger import logger
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class PermService:
    @staticmethod
    async def get_by_user_id(
        db: AsyncSession, user_id: PositiveInt
    ) -> list[schemas.PermOut]:
        try:
            perms = await cruds.PermCrud.get_by_user_id(db=db, user_id=user_id)

            if perms is None:  # "not perms" won't work as expected
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuário com ID {user_id} não encontrado",
                )

            return [schemas.PermOut.model_validate(p) for p in perms]
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            msg = f"Erro no banco de dados ao buscar permissões do usuário"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
        except Exception as e:
            msg = f"Erro inesperado ao buscar permissões do usuário {user_id}"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
