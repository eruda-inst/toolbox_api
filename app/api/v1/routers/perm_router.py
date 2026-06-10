from typing import Annotated
from pydantic import PositiveInt
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from .. import db, models, deps, services, schemas

perm_router = APIRouter(prefix="/permissoes", tags=["Permissões"])

db_dep = Annotated[AsyncSession, Depends(db.get_db)]
current_user_dep = Annotated[models.User, Depends(deps.get_current_user)]


@perm_router.get(path="/usuario/id/{id}", summary="Retorna permissões de um usuário")
async def get_by_user_id(
    db: db_dep,
    current_user: current_user_dep,
    id: Annotated[PositiveInt, Path(description="ID do usuário")],
) -> list[schemas.PermOut]:
    """
    Retorna permissões associadas a um usuário, através de seu ID
    """
    return await services.PermService.get_by_user_id(db=db, user_id=id)


@perm_router.get(path="/grupo/id/{id}", summary="Retorna permissões de um grupo")
async def get_by_group_id(
    db: db_dep,
    current_user: current_user_dep,
    id: Annotated[PositiveInt, Path(description="ID do grupo")],
) -> list[schemas.PermOut]:
    """
    Retorna permissões associadas a um grupo, através de seu ID
    """
    return await services.PermService.get_by_group_id(db=db, group_id=id)
