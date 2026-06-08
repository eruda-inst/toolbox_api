from typing import Annotated
from fastapi.logger import logger
from .. import db, services, models, utils
from sqlalchemy.ext.asyncio import AsyncSession
from .authentication_dep import get_current_user
from fastapi import HTTPException, status, Depends

db_dep = Annotated[AsyncSession, Depends(db.get_db)]
current_user_dep = Annotated[models.User, Depends(get_current_user)]


def has_perm(required_perm: utils.PermCodes):
    async def dep(db: db_dep, current_user: current_user_dep) -> models.User:
        try:
            perms = await services.PermService.get_by_user_id(
                db=db, user_id=current_user.id  # type: ignore
            )

            # Use set for O(1) membership test
            perm_codes = {p.codigo for p in perms}

            if required_perm not in perm_codes:
                logger.warning(
                    f"Usuário {current_user.id} (e-mail: {current_user.email}) tentou acessar recurso sem permissão: {required_perm}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão necessária: {required_perm}",
                )

            return current_user
        except HTTPException:
            raise
        except Exception as e:
            msg = (
                f"Erro inesperado ao verificar permissão para usuário {current_user.id}"
            )
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

    return dep
