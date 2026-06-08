from typing import Annotated
from .. import schemas, db, services
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

authentication_router = APIRouter(tags=["Autenticação"], prefix="/autenticacao")


db_dep = Annotated[AsyncSession, Depends(dependency=db.get_db)]


@authentication_router.post(path="/login", summary="Autenticação de usuário")
async def login(
    db: db_dep,
    credenciais: Annotated[
        schemas.LoginCreds, Body(description="Credenciais de login")
    ],
) -> schemas.AccessTokenOut:
    """
    Autenticação de usuário para acessar o sistema
    """
    return await services.AuthenticationService.login(creds=credenciais, db=db)


@authentication_router.post(path="/refresh-token", summary="Renova token de acesso")
async def refresh_token(
    db: db_dep,
    refresh_token: Annotated[str, Body(embed=True, description="Token de atualização")],
) -> schemas.AccessTokenOut:
    """
    Renova token de acesso do usuário
    """
    return await services.AuthenticationService.refresh_token(
        refresh_token=refresh_token, db=db
    )
