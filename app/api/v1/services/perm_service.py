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
            user = await cruds.UserCrud.get_by_id(db=db, id=user_id, load_perms=True)

            if user is None:
                msg = f"Usuário com ID {user_id} não encontrado"
                logger.warning(msg)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

            perms = user.grupo.permissoes

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

    @staticmethod
    async def get_by_group_id(
        db: AsyncSession, group_id: PositiveInt
    ) -> list[schemas.PermOut]:
        try:
            group = await cruds.GroupCrud.get_by_id(db=db, id=group_id)

            if group is None:
                msg = f"Grupo com ID {group_id} não encontrado"
                logger.warning(msg)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

            perms = group.permissoes

            return [schemas.PermOut.model_validate(p) for p in perms]
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            msg = f"Erro no banco de dados ao buscar permissões do grupo"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
        except Exception as e:
            msg = f"Erro inesperado ao buscar permissões do grupo {group_id}"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

    @staticmethod
    async def get_by_group_name(
        db: AsyncSession, group_name: str
    ) -> list[schemas.PermOut]:
        try:
            group = await cruds.GroupCrud.get_by_name(db=db, name=group_name)

            if group is None:
                msg = f"Grupo com nome {group_name} não encontrado"
                logger.warning(msg)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

            perms = group.permissoes

            return [schemas.PermOut.model_validate(p) for p in perms]
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            msg = f"Erro no banco de dados ao buscar permissões do grupo"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
        except Exception as e:
            msg = f"Erro inesperado ao buscar permissões do grupo {group_name}"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
